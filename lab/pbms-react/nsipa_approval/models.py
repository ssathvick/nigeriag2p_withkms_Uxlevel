"""Persistent, export-only approval flow on native PBMS programmes and lists."""
import base64, calendar, hashlib, io, json, math
from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

PREFIX = 'nsipa_approval.'
STAGES = [(1, 'Finance', 'group_finance'), (2, 'Audit', 'group_audit'), (3, 'CEO', 'group_ceo')]

def is_admin(env):
    return env.user.has_group(PREFIX+'group_admin') or env.user.has_group('g2p_pbms.group_program_super_administration')

def access_program(program):
    program.check_access_rights('read'); program.check_access_rule('read')
    # PBMS programme access uses the programme-specific user group.
    if not is_admin(program.env) and program.program_mnemonic not in program.env.user.groups_id.mapped('name'):
        raise AccessError('You are not assigned to this programme.')

def admin_program(program):
    access_program(program)
    if not is_admin(program.env): raise AccessError('Programme Admin permission is required.')

class Program(models.Model):
    _inherit = 'g2p.program.definition'
    nsipa_flow = fields.Boolean('Programme to disbursement approval flow', default=False, copy=False)
    nsipa_setup_ready = fields.Boolean('Programme setup complete', default=False, copy=False, readonly=True)
    nsipa_stage_ids = fields.One2many('nsipa.approval.stage', 'program_id', string='Sequential approval stages')

    @api.model
    def create(self, vals):
        if vals.get('nsipa_flow'):
            if vals.get('target_registry') not in ['household','farmer','student']:raise ValidationError('Select Households, Farmers or Students as the base registry.')
            if not is_admin(self.env): raise AccessError('Programme Admin permission is required.')
            vals = dict(vals, verifications_for_enrolment=0, auto_approve_enrolment=True,
                        verifications_for_disbursement=3, auto_approve_disbursement=False,
                        enrollment_frequency='Monthly', disbursement_frequency='Monthly', nsipa_setup_ready=False)
        if vals.get('nsipa_setup_ready') or vals.get('nsipa_stage_ids'): raise AccessError('Use the programme setup action.')
        if vals.get('nsipa_flow'):
            allowed={'program_mnemonic','description','target_registry','program_status','service_providers_required','nsipa_flow','enrollment_frequency','disbursement_frequency','verifications_for_enrolment','auto_approve_enrolment','verifications_for_disbursement','auto_approve_disbursement','nsipa_setup_ready'}
            if set(vals)-allowed:raise AccessError('Unsupported programme setup fields.')
            self.check_access_rights('create')
            return super(Program,self.sudo()).create(vals).with_env(self.env)
        return super().create(vals)

    def write(self, vals):
        if {'nsipa_setup_ready','nsipa_stage_ids'} & vals.keys() and not self.env.su:
            raise AccessError('Use the programme setup action.')
        for p in self:
            if p.nsipa_flow or vals.get('nsipa_flow'):
                if not self.env.su: admin_program(p)
                if 'program_mnemonic' in vals and vals['program_mnemonic']!=p.program_mnemonic:raise UserError('The programme identifier cannot change after creation.')
                if p.beneficiary_list_ids and set(vals)-{'description','program_status'}:
                    raise UserError('Programme settings are locked once a list exists. Create another programme for changed rules.')
                policy={'verifications_for_enrolment':0,'auto_approve_enrolment':True,'verifications_for_disbursement':3,'auto_approve_disbursement':False,'enrollment_frequency':'Monthly','disbursement_frequency':'Monthly'}
                for k,v in policy.items():
                    if k in vals and vals[k]!=v: raise ValidationError('This flow requires monthly cycles, automatic enrolment, and Finance, Audit, CEO approval.')
                if 'nsipa_flow' in vals and not vals['nsipa_flow']: raise ValidationError('Approval flow cannot be disabled after activation.')
        return super().write(vals)

    def nsipa_configure(self, benefit_id, eligibility_domain, quantity, group_ids=None):
        self.ensure_one(); admin_program(self)
        self.env.cr.execute('SELECT id FROM g2p_program_definition WHERE id=%s FOR UPDATE',[self.id])
        if not self.nsipa_flow or self.beneficiary_list_ids: raise UserError('Configure an approval-flow programme before creating lists.')
        if self.program_status!='ACTIVE': raise ValidationError('Activate the programme before completing setup.')
        benefit=self.env['g2p.benefit.codes'].browse(int(benefit_id)).exists()
        benefit.check_access_rights('read'); benefit.check_access_rule('read')
        if not benefit or benefit.benefit_type not in ['CASH_DIGITAL','CASH_PHYSICAL'] or benefit.measurement_unit.upper()!='NGN':
            raise ValidationError('Select a cash Benefit Code with measurement unit NGN.')
        quantity=float(quantity)
        if not math.isfinite(quantity) or not 0<quantity<=25000: raise ValidationError('Entitlement must be above zero and no greater than NGN 25,000.')
        registry=self.env['g2p.%s.registry'%self.target_registry]
        domain=safe_eval(eligibility_domain or '[]')
        if not isinstance(domain,list): raise ValidationError('Eligibility criteria must be a valid registry filter.')
        registry.search(domain,limit=1)
        ids=group_ids or [self.env.ref(PREFIX+g).id for _,_,g in STAGES]
        if len(ids)!=3 or len(set(ids))!=3: raise ValidationError('Choose three distinct approval groups: Finance, Audit, CEO.')
        groups=self.env['res.groups'].browse([int(i) for i in ids]).exists()
        if len(groups)!=3: raise ValidationError('An approval group does not exist.')
        self.sudo().nsipa_stage_ids.unlink()
        for (sequence,name,_),gid in zip(STAGES,ids):
            self.env['nsipa.approval.stage'].sudo().create({'program_id':self.id,'sequence':sequence,'name':name,'group_id':int(gid)})
        mapping=self.env['g2p.program.benefit.codes'].search([('program_id','=',self.id)])
        rules=self.env['g2p.entitlement.rule.definition'].search([('program_id','=',self.id)])
        elig=self.env['g2p.eligibility.rule.definition'].search([('program_id','=',self.id)])
        mapping.unlink();rules.unlink();elig.unlink()
        self.env['g2p.program.benefit.codes'].create({'program_id':self.id,'benefit_code_id':benefit.id,'max_quantity':25000})
        self.env['g2p.eligibility.rule.definition'].create({'program_id':self.id,'target_registry':self.target_registry,'mnemonic':self.program_mnemonic+'_ELIG','rule_number':1,'set_operator':'NONE','pbms_domain':repr(domain)})
        self.env['g2p.entitlement.rule.definition'].create({'program_id':self.id,'target_registry':self.target_registry,'mnemonic':self.program_mnemonic+'_CASH','benefit_code_id':benefit.id,'quantity':quantity,'pbms_domain':repr(domain)})
        self.sudo().write({'nsipa_setup_ready':True})
        return True

class Stage(models.Model):
    _name='nsipa.approval.stage'
    _description='Programme approval level'
    _order='sequence,id'
    program_id=fields.Many2one('g2p.program.definition',required=True,ondelete='cascade')
    sequence=fields.Integer(required=True)
    name=fields.Char(required=True)
    group_id=fields.Many2one('res.groups',required=True)
    _sql_constraints=[('level_unique','unique(program_id,sequence)','Approval level must be unique.')]

class Enrollment(models.Model):
    _inherit='g2p.enrollment.cycle'
    @api.model
    def create(self,vals):
        p=self.env['g2p.program.definition'].browse(vals.get('program_id'))
        if p.nsipa_flow:
            admin_program(p)
            self.env.cr.execute('SELECT id FROM g2p_program_definition WHERE id=%s FOR UPDATE',[p.id])
            if not p.nsipa_setup_ready: raise UserError('Complete programme setup first.')
            start=fields.Date.to_date(vals.get('enrollment_start_date'));end=fields.Date.to_date(vals.get('enrollment_end_date'))
            ds=fields.Date.to_date(vals.get('disbursement_start_date'));de=fields.Date.to_date(vals.get('disbursement_end_date'))
            if not start or not end or not ds or not de or not start<=end<ds<=de:
                raise ValidationError('Registration must end before the disbursement window begins.')
            if (ds.year,ds.month)!=(de.year,de.month): raise ValidationError('Disbursement dates must be in one monthly cycle.')
            if self.search_count([('program_id','=',p.id),('disbursement_start_date','>=',ds.replace(day=1)),('disbursement_start_date','<=',ds.replace(day=calendar.monthrange(ds.year,ds.month)[1]))]):
                raise ValidationError('This programme already has an enrolment cycle for the month.')
        return super().create(vals)
    def write(self,vals):
        for c in self:
            if c.program_id.nsipa_flow and not self.env.su:
                admin_program(c.program_id)
                if c.beneficiary_list_ids or 'approved_for_enrollment' in vals: raise UserError('Cycle workflow fields are controlled by list processing.')
        return super().write(vals)

class Disbursement(models.Model):
    _inherit='g2p.disbursement.cycle'
    nsipa_enrollment_cycle_id=fields.Many2one('g2p.enrollment.cycle',string='Approved enrolment cycle')
    @api.model
    def create(self,vals):
        p=self.env['g2p.program.definition'].browse(vals.get('program_id'))
        if p.nsipa_flow:
            admin_program(p)
            self.env.cr.execute('SELECT id FROM g2p_program_definition WHERE id=%s FOR UPDATE',[p.id])
            e=self.env['g2p.enrollment.cycle'].browse(vals.get('nsipa_enrollment_cycle_id')).exists()
            if not e or e.program_id!=p or not e.approved_for_enrollment: raise ValidationError('Select a completed, approved enrolment cycle from this programme.')
            date=fields.Date.to_date(vals.get('disbursement_schedule_date'))
            if not date or not e.disbursement_start_date<=date<=e.disbursement_end_date: raise ValidationError('Schedule date must fall within the enrolment cycle disbursement window.')
            if self.search_count([('program_id','=',p.id),('nsipa_enrollment_cycle_id','=',e.id)]): raise ValidationError('A disbursement cycle already exists for this monthly enrolment cycle.')
        return super().create(vals)
    def write(self,vals):
        for c in self:
            if c.program_id.nsipa_flow and not self.env.su:
                admin_program(c.program_id)
                if c.beneficiary_list_ids or 'approved_for_disbursement' in vals: raise UserError('Cycle workflow fields are controlled by the approval flow.')
        return super().write(vals)

class ApprovalLine(models.Model):
    _name='nsipa.approval.line'
    _description='Persistent beneficiary list entry'
    _order='id'
    list_id=fields.Many2one('g2p.beneficiary.list',required=True,ondelete='cascade',index=True)
    registry_id=fields.Integer(required=True)
    beneficiary_id=fields.Char(required=True)
    name=fields.Char()
    state=fields.Char()
    amount=fields.Float(digits=(16,2))
    included=fields.Boolean(default=True)
    source_json=fields.Text()
    _sql_constraints=[('person_unique','unique(list_id,beneficiary_id)','A beneficiary may appear only once in a list.')]
    def read(self,fields=None,load='_classic_read'):
        for p in self.mapped('list_id.program_id'):access_program(p)
        return super().read(fields,load)

class Event(models.Model):
    _name='nsipa.approval.event'
    _description='Immutable approval and correction history'
    _order='id'
    list_id=fields.Many2one('g2p.beneficiary.list',required=True,ondelete='restrict',index=True)
    revision=fields.Integer(required=True)
    stage=fields.Char(required=True)
    decision=fields.Char(required=True)
    comment=fields.Text(required=True)
    approver_id=fields.Many2one('res.users',required=True)
    recorded_at=fields.Datetime(default=fields.Datetime.now,required=True)
    attachment=fields.Binary(attachment=False)
    filename=fields.Char()
    content_hash=fields.Char()
    def read(self,fields=None,load='_classic_read'):
        for p in self.mapped('list_id.program_id'):access_program(p)
        return super().read(fields,load)

class BeneficiaryList(models.Model):
    _inherit='g2p.beneficiary.list'
    nsipa_status=fields.Selection([('pending','Pending'),('processing','Processing'),('complete','Complete'),('finance','Awaiting Finance'),('audit','Awaiting Audit'),('ceo','Awaiting CEO'),('rejected','Returned for correction'),('verified','Fully verified'),('error','Processing failed')],readonly=True,copy=False)
    nsipa_revision=fields.Integer(default=1,readonly=True,copy=False)
    nsipa_error=fields.Text(readonly=True,copy=False)
    nsipa_line_ids=fields.One2many('nsipa.approval.line','list_id')
    nsipa_event_ids=fields.One2many('nsipa.approval.event','list_id')
    nsipa_total=fields.Float(compute='_nsipa_total')
    @api.depends('nsipa_line_ids.amount','nsipa_line_ids.included')
    def _nsipa_total(self):
        for r in self:r.nsipa_total=sum(r.nsipa_line_ids.filtered('included').mapped('amount'))

    @api.model
    def create(self,vals):
        e=self.env['g2p.enrollment.cycle'].browse(vals.get('enrollment_cycle_id'))
        d=self.env['g2p.disbursement.cycle'].browse(vals.get('disbursement_cycle_id'))
        p=(e.program_id or d.program_id)
        if p.nsipa_flow:
            admin_program(p)
            if bool(e)==bool(d):raise ValidationError('Select exactly one cycle.')
            if p.program_status!='ACTIVE':raise UserError('The programme must be Active before creating a list.')
            if not p.nsipa_setup_ready:raise UserError('Complete programme setup first.')
            if e and e.enrollment_end_date>=fields.Date.context_today(self): raise UserError('Create the enrolment list after the registration window closes.')
            cycle_field='enrollment_cycle_id' if e else 'disbursement_cycle_id';cycle=e or d
            self.env.cr.execute('SELECT id FROM '+('g2p_enrollment_cycle' if e else 'g2p_disbursement_cycle')+' WHERE id=%s FOR UPDATE',[cycle.id])
            if self.search_count([(cycle_field,'=',cycle.id)]):raise UserError('A list already exists for this cycle. Open it instead.')
            if d and not d.nsipa_enrollment_cycle_id.approved_for_enrollment:raise UserError('Enrolment must be complete first.')
            blocked=set(vals)&{'nsipa_status','nsipa_line_ids','nsipa_event_ids','nsipa_revision','list_workflow_status','approval_date','number_of_registrants','number_of_entitlements_processed'}
            if blocked:raise AccessError('Workflow fields are server controlled.')
            vals=dict(vals,nsipa_status='pending',eligibility_process_status='not_applicable',entitlement_process_status='not_applicable',envelope_creation_status='not_applicable',disbursement_batch_creation_status='not_applicable')
        return super().create(vals)

    def write(self,vals):
        for r in self:
            if r.program_id.nsipa_flow and not self.env.su:
                admin_program(r.program_id)
                if set(vals)-{'brief','mnemonic'} or r.nsipa_status not in ['pending','complete','rejected','error']:
                    raise AccessError('Use the role-checked workflow actions to change this list.')
        return super().write(vals)

    def unlink(self):
        if any(r.program_id.nsipa_flow for r in self):raise UserError('Approval-flow lists and their audit history must be retained.')
        return super().unlink()

    def _nsipa_lock(self):
        self.ensure_one();self.check_access_rights('read');self.check_access_rule('read');access_program(self.program_id)
        if not self.program_id.nsipa_flow:raise UserError('This list does not use the sequential approval flow.')
        self.env.cr.execute('SELECT id FROM g2p_beneficiary_list WHERE id=%s FOR UPDATE',[self.id]);self.invalidate_recordset()

    def _nsipa_hash(self):
        return hashlib.sha256(json.dumps([(l.beneficiary_id,l.amount,l.included) for l in self.nsipa_line_ids],sort_keys=True).encode()).hexdigest()

    def _nsipa_event(self,stage,decision,comment,attachment=None,filename=None):
        vals={'list_id':self.id,'revision':self.nsipa_revision,'stage':stage,'decision':decision,'comment':comment,'approver_id':self.env.uid,'content_hash':self._nsipa_hash()}
        if attachment:
            try:raw=base64.b64decode(attachment,validate=True)
            except Exception:raise ValidationError('Invalid document encoding.')
            if len(raw)>10*1024*1024:raise ValidationError('Supporting documents must be no larger than 10 MB.')
            vals.update(attachment=attachment,filename=(filename or 'supporting-document').replace('/','_').replace('\\','_'))
        self.env['nsipa.approval.event'].sudo().create(vals)

    @api.model
    def _nsipa_process_pending(self):
        for listing in self.sudo().search([('program_id.nsipa_flow','=',True),('nsipa_status','=','pending')],limit=5):
            self.env.cr.execute('SELECT id FROM g2p_beneficiary_list WHERE id=%s FOR UPDATE SKIP LOCKED',[listing.id])
            if not self.env.cr.fetchone():continue
            try:
                with self.env.cr.savepoint():listing._nsipa_calculate()
            except Exception as exc:
                listing.sudo().write({'nsipa_status':'error','nsipa_error':str(exc)[:1000]})

    def _nsipa_calculate(self):
        self.ensure_one();self.write({'nsipa_status':'processing','nsipa_error':False})
        owner=self.with_user(self.create_uid);p=owner.program_id;access_program(p)
        registry=owner.env['g2p.%s.registry'%p.target_registry]
        rules=p.eligibility_rule_ids.sorted('rule_number');selected=registry.browse()
        if not rules:raise UserError('No eligibility rule is configured.')
        for rule in rules:
            found=registry.search(safe_eval(rule.pbms_domain or '[]'))
            if rule.set_operator in ['NONE','UNION']:selected|=found
            elif rule.set_operator=='INTERSECT':selected&=found
            elif rule.set_operator=='EXCEPT':selected-=found
        if self.list_stage=='disbursement':
            source=self.disbursement_cycle_id.nsipa_enrollment_cycle_id.beneficiary_list_ids.filtered(lambda r:r.nsipa_status=='complete')
            enrolled=set(source.nsipa_line_ids.filtered('included').mapped('beneficiary_id'))
            selected=selected.filtered(lambda r:r.link_registry_id in enrolled)
        if not selected:raise UserError('No eligible registry beneficiaries were found. Review the programme criteria.')
        commands=[]
        for r in selected:
            if not r.link_registry_id:raise UserError('An eligible registry record has no beneficiary identifier.')
            amount=0
            if self.list_stage=='disbursement':
                for rule in p.entitlement_rule_ids:
                    if registry.search_count(expression.AND([[('id','=',r.id)],safe_eval(rule.pbms_domain or '[]')])):
                        value=rule.quantity*(r[rule.multiplier] if rule.multiplier else 1)
                        maximum=p.program_benefit_code_ids.filtered(lambda m:m.benefit_code_id==rule.benefit_code_id)
                        if len(maximum)!=1 or maximum.max_quantity!=25000:raise UserError('Benefit mapping maximum must be NGN 25,000.')
                        if not math.isfinite(value) or value<0 or value>maximum.max_quantity:raise UserError('A calculated entitlement exceeds its programme maximum.')
                        amount+=value
                if not math.isfinite(amount) or not 0<amount<=25000:raise UserError('Every beneficiary must have a positive entitlement no greater than NGN 25,000.')
            commands.append((0,0,{'registry_id':r.id,'beneficiary_id':r.link_registry_id,'name':r.name or r.link_registry_id,'state':r.large_area_code,'amount':amount,'source_json':json.dumps(r.read(['link_registry_id','name','large_area_code'])[0],default=str)}))
        self.write({'nsipa_line_ids':commands,'nsipa_status':'complete','eligibility_process_status':'complete','entitlement_process_status':'complete' if self.list_stage=='disbursement' else 'not_applicable','number_of_registrants':len(commands),'number_of_entitlements_processed':len(commands) if self.list_stage=='disbursement' else 0})
        if self.list_stage=='enrollment':
            self.write({'list_workflow_status':'approved_final_enrolment','approval_date':fields.Date.context_today(self)})
            self.enrollment_cycle_id.sudo().write({'approved_for_enrollment':True})

    def nsipa_submit(self,comment=''):
        self._nsipa_lock()
        if not self.env.user.has_group(PREFIX+'group_payment'):raise AccessError('Payment permission is required to initiate approval.')
        if self.list_stage!='disbursement' or self.nsipa_status not in ['complete','rejected']:raise UserError('Only a complete or corrected disbursement list can be submitted.')
        lines=self.nsipa_line_ids.filtered('included')
        if not lines or any(not math.isfinite(l.amount) or not 0<l.amount<=25000 for l in lines):raise ValidationError('Review the beneficiary list and entitlements before submitting.')
        if self.nsipa_status=='rejected':self.sudo().write({'nsipa_revision':self.nsipa_revision+1})
        self._nsipa_event('Payment','Submitted',str(comment).strip() or 'Submitted for sequential approval.')
        self.sudo().write({'nsipa_status':'finance'})
        return True

    def nsipa_decide(self,decision,comment,attachment=None,filename=None):
        self._nsipa_lock()
        if self.nsipa_status not in ['finance','audit','ceo']:raise UserError('This list is not awaiting an approval.')
        stage=self.program_id.nsipa_stage_ids.filtered(lambda s:s.sequence=={'finance':1,'audit':2,'ceo':3}[self.nsipa_status])
        if len(stage)!=1 or stage.group_id not in self.env.user.groups_id:raise AccessError('Only the assigned %s group can review this level.'%self.nsipa_status.title())
        if decision not in ['approve','reject'] or not str(comment).strip():raise ValidationError('Choose Approve or Reject and enter comments.')
        current=self.nsipa_event_ids.filtered(lambda e:e.revision==self.nsipa_revision and e.decision=='Approved')
        if self.env.uid in current.mapped('approver_id').ids:raise AccessError('Each level requires an independent approver.')
        self._nsipa_event(stage.name,'Approved' if decision=='approve' else 'Rejected',comment,attachment,filename)
        status='rejected' if decision=='reject' else {'finance':'audit','audit':'ceo','ceo':'verified'}[self.nsipa_status]
        # Do NOT set approved_for_disbursement: that legacy flag starts the Bridge payment pipeline.
        self.sudo().write({'nsipa_status':status,'approval_date':fields.Date.context_today(self) if status=='verified' else False})
        return True

    def nsipa_correct(self,line_id,amount,included,comment):
        self._nsipa_lock();admin_program(self.program_id)
        if self.list_stage!='disbursement' or self.nsipa_status not in ['complete','rejected']:raise UserError('Corrections are available before submission or after rejection.')
        line=self.nsipa_line_ids.filtered(lambda l:l.id==int(line_id));amount=float(amount)
        if not line or not math.isfinite(amount) or not 0<amount<=25000 or not str(comment).strip():raise ValidationError('Select a beneficiary, enter an amount up to NGN 25,000 and a correction reason.')
        before={'amount':line.amount,'included':line.included};line.sudo().write({'amount':amount,'included':bool(included)})
        self._nsipa_event('Programme Admin','Corrected',str(comment)+' | '+json.dumps({'beneficiary':line.beneficiary_id,'before':before,'after':{'amount':amount,'included':bool(included)}}))
        self.sudo().write({'number_of_registrants':len(self.nsipa_line_ids.filtered('included'))})
        return True

    def nsipa_retry(self):
        self._nsipa_lock();admin_program(self.program_id)
        if self.nsipa_status!='error':raise UserError('Only failed processing can be retried.')
        self.sudo().write({'nsipa_status':'pending','nsipa_error':False})
        return True

    @api.model
    def nsipa_identity(self):
        return {'name':self.env.user.name,'uid':self.env.uid,'admin':is_admin(self.env),'payment':self.env.user.has_group(PREFIX+'group_payment'),'roles':[name for _,name,g in STAGES if self.env.user.has_group(PREFIX+g)]}

    def nsipa_details(self):
        self.ensure_one();access_program(self.program_id)
        names=['mnemonic','program_id','list_stage','enrollment_cycle_id','disbursement_cycle_id','nsipa_status','nsipa_revision','nsipa_error','number_of_registrants','nsipa_total']
        line_fields=['beneficiary_id','name','state','amount','included','registry_id']
        events=self.nsipa_event_ids.read(['revision','stage','decision','comment','approver_id','recorded_at','filename','content_hash'])
        current=self.program_id.nsipa_stage_ids.filtered(lambda s:s.sequence=={'finance':1,'audit':2,'ceo':3}.get(self.nsipa_status,0))
        return {'list':self.read(names)[0],'lines':self.nsipa_line_ids.read(line_fields),'history':events,'can_decide':bool(current and current.group_id in self.env.user.groups_id),'identity':self.nsipa_identity()}

    def nsipa_attachment(self,event_id):
        self.ensure_one();access_program(self.program_id)
        e=self.nsipa_event_ids.filtered(lambda e:e.id==int(event_id))
        if not e or not e.attachment:raise UserError('The supporting document is unavailable.')
        return {'filename':e.filename,'data':e.attachment.decode() if isinstance(e.attachment,bytes) else e.attachment}

    def nsipa_export(self):
        self._nsipa_lock();admin_program(self.program_id)
        if self.nsipa_status!='verified':raise AccessError('Export is available only after all three approvals.')
        checks=self.nsipa_event_ids.filtered(lambda e:e.revision==self.nsipa_revision and e.decision=='Approved')
        if set(checks.mapped('stage'))!={'Finance','Audit','CEO'} or len(set(checks.mapped('approver_id').ids))!=3 or any(e.content_hash!=self._nsipa_hash() for e in checks):raise AccessError('The current list does not have three valid independent approvals.')
        import xlwt
        book=xlwt.Workbook();headers=['Beneficiary ID','Name','State','Amount NGN','Programme','Disbursement cycle','Revision']
        sheet=None
        for index,line in enumerate(self.nsipa_line_ids.filtered('included')):
            row=index%65535+1
            if row==1:
                sheet=book.add_sheet('Beneficiaries '+str(index//65535+1))
                for col,h in enumerate(headers):sheet.write(0,col,h);sheet.col(col).width=6000
            for j,v in enumerate([line.beneficiary_id,line.name,line.state or '',line.amount,self.program_id.program_mnemonic,self.disbursement_cycle_id.cycle_mnemonic,self.nsipa_revision]):sheet.write(row,j,v)
        out=io.BytesIO();book.save(out);self._nsipa_event('Programme Admin','Exported','Final beneficiary list exported in native XLS format.')
        return {'filename':'NSIPA-beneficiaries-%s-r%s.xls'%(self.id,self.nsipa_revision),'data':base64.b64encode(out.getvalue()).decode()}

class Wizard(models.TransientModel):
    _inherit='g2p.bgtask.summary.wizard'
    def approve_for_disbursement(self):
        if any(w.program_id.nsipa_flow for w in self):raise AccessError('Use the Finance, Audit and CEO approval flow. Payment dispatch is outside this flow.')
        return super().approve_for_disbursement()

# Configuration is mutable only before the programme has any lists.
def guard_configuration(record,values=None):
    p=record.program_id
    if p.nsipa_flow:
        admin_program(p)
        if p.beneficiary_list_ids:raise UserError('Programme rules and benefit mappings are locked after list creation.')

class Mapping(models.Model):
    _inherit='g2p.program.benefit.codes'
    @api.constrains('max_quantity','program_id','benefit_code_id')
    def _nsipa_cap(self):
        for r in self:
            if r.program_id.nsipa_flow and (r.max_quantity!=25000 or r.benefit_code_id.measurement_unit.upper()!='NGN' or r.benefit_code_id.benefit_type not in ['CASH_DIGITAL','CASH_PHYSICAL']):raise ValidationError('Approval-flow cash benefits require NGN and Maximum Quantity 25,000.')
    @api.model
    def create(self,vals):
        p=self.env['g2p.program.definition'].browse(vals.get('program_id'))
        if p.nsipa_flow:
            admin_program(p)
            if p.beneficiary_list_ids:raise UserError('Programme mappings are locked after list creation.')
        return super().create(vals)
    def write(self,vals):
        if vals.get('program_id'):
            target=self.env['g2p.program.definition'].browse(vals['program_id'])
            if target.nsipa_flow:
                admin_program(target)
                if target.beneficiary_list_ids:raise UserError('Programme configuration is locked after list creation.')
        for r in self:guard_configuration(r)
        return super().write(vals)
    def unlink(self):
        for r in self:guard_configuration(r)
        return super().unlink()

class Eligibility(models.Model):
    _inherit='g2p.eligibility.rule.definition'
    @api.model
    def create(self,vals):
        p=self.env['g2p.program.definition'].browse(vals.get('program_id'))
        if p.nsipa_flow:
            admin_program(p)
            if p.beneficiary_list_ids:raise UserError('Programme eligibility rules are locked after list creation.')
        return super().create(vals)
    def write(self,vals):
        if vals.get('program_id'):
            target=self.env['g2p.program.definition'].browse(vals['program_id'])
            if target.nsipa_flow:
                admin_program(target)
                if target.beneficiary_list_ids:raise UserError('Programme configuration is locked after list creation.')
        for r in self:guard_configuration(r)
        return super().write(vals)
    def unlink(self):
        for r in self:guard_configuration(r)
        return super().unlink()

class Entitlement(models.Model):
    _inherit='g2p.entitlement.rule.definition'
    @api.constrains('quantity','program_id')
    def _nsipa_quantity(self):
        for r in self:
            if r.program_id.nsipa_flow and (not math.isfinite(r.quantity) or not 0<r.quantity<=25000):raise ValidationError('Entitlement must be above zero and no greater than NGN 25,000.')
    @api.model
    def create(self,vals):
        p=self.env['g2p.program.definition'].browse(vals.get('program_id'))
        if p.nsipa_flow:
            admin_program(p)
            if p.beneficiary_list_ids:raise UserError('Programme entitlement rules are locked after list creation.')
        return super().create(vals)
    def write(self,vals):
        if vals.get('program_id'):
            target=self.env['g2p.program.definition'].browse(vals['program_id'])
            if target.nsipa_flow:
                admin_program(target)
                if target.beneficiary_list_ids:raise UserError('Programme configuration is locked after list creation.')
        for r in self:guard_configuration(r)
        return super().write(vals)
    def unlink(self):
        for r in self:guard_configuration(r)
        return super().unlink()

class ProgramWorkspace(models.Model):
    _inherit='g2p.program.definition'
    @api.model
    def nsipa_options(self):
        result={'registries':[(v,n) for v,n in self._fields['target_registry'].selection if v in ['household','farmer','student']],'groups':[],'defaults':{}}
        if callable(result['registries']):result['registries']=result['registries'](self)
        if is_admin(self.env):
            result['groups']=self.env['res.groups'].sudo().search_read([('share','=',False)],['name'],order='name')
            result['defaults']={name:self.env.ref(PREFIX+g).id for _,name,g in STAGES}
        return result

    def nsipa_workspace(self):
        self.ensure_one();access_program(self)
        lists=self.beneficiary_list_ids.read(['mnemonic','list_stage','enrollment_cycle_id','disbursement_cycle_id','nsipa_status','nsipa_revision','number_of_registrants','creation_date'])
        return {'program':self.read(['program_mnemonic','description','target_registry','program_status','nsipa_setup_ready'])[0],
          'stages':self.nsipa_stage_ids.read(['sequence','name','group_id']),
          'benefits':self.program_benefit_code_ids.read(['benefit_code_id','max_quantity']),
          'eligibility':self.eligibility_rule_ids.read(['mnemonic','pbms_domain']),
          'entitlements':self.entitlement_rule_ids.read(['mnemonic','quantity']),
          'enrollment':self.enrollment_cycle_ids.read(['cycle_number','enrollment_start_date','enrollment_end_date','disbursement_start_date','disbursement_end_date','approved_for_enrollment']),
          'disbursement':self.disbursement_cycle_ids.read(['cycle_mnemonic','disbursement_schedule_date','nsipa_enrollment_cycle_id']),
          'lists':lists,
          'members':self._nsipa_members() if is_admin(self.env) else []}

    def _nsipa_members(self):
        group=self.env['res.groups'].sudo().search([('name','=',self.program_mnemonic)],limit=1)
        return [{'id':u.id,'name':u.name,'login':u.login,'roles':[name for name,g in [('Programme Admin','group_admin'),('Payment','group_payment')]+[(n,g) for _,n,g in STAGES] if self.env.ref(PREFIX+g) in u.groups_id]} for u in group.users if u.active and not u.share]

    def nsipa_assign_role(self,user_id,role):
        self.ensure_one();admin_program(self)
        if not self.env.user.has_group('base.group_system'):raise AccessError('Only a staff access administrator can assign approval roles.')
        mapping={'Programme Admin':'group_admin','Payment':'group_payment','Finance':'group_finance','Audit':'group_audit','CEO':'group_ceo'}
        if role not in mapping:raise ValidationError('Choose an approval-flow role.')
        user=self.env['res.users'].sudo().browse(int(user_id)).exists()
        if not user or not user.active or user.share:raise ValidationError('Select an active internal staff account.')
        program_group=self.env['res.groups'].sudo().search([('name','=',self.program_mnemonic)],limit=1)
        user.write({'groups_id':[(4,program_group.id),(4,self.env.ref(PREFIX+mapping[role]).id)]})
        return True

class ListReadGuard(models.Model):
    _inherit='g2p.beneficiary.list'
    def read(self,fields=None,load='_classic_read'):
        for r in self:
            if r.program_id.nsipa_flow:access_program(r.program_id)
        return super().read(fields,load)
    def action_open_summary_wizard(self):
        if self.program_id.nsipa_flow:
            access_program(self.program_id)
            return {'type':'ir.actions.act_url','url':'/pbms-ui/#programme-flow?program_id=%s'%self.program_id.id,'target':'self'}
        return super().action_open_summary_wizard()




class MonthlyEnrollmentGuards(models.Model):
    _inherit='g2p.enrollment.cycle'
    @api.constrains('program_id','enrollment_start_date','enrollment_end_date','disbursement_start_date','disbursement_end_date')
    def _nsipa_dates(self):
        for c in self.filtered(lambda c:c.program_id.nsipa_flow):
            if not c.enrollment_start_date<=c.enrollment_end_date<c.disbursement_start_date<=c.disbursement_end_date:
                raise ValidationError('Registration must end before the disbursement window begins.')
            ds,de=c.disbursement_start_date,c.disbursement_end_date
            if (ds.year,ds.month)!=(de.year,de.month):raise ValidationError('Disbursement dates must belong to one monthly cycle.')
            if self.search_count([('program_id','=',c.program_id.id),('id','!=',c.id),('disbursement_start_date','>=',ds.replace(day=1)),('disbursement_start_date','<=',ds.replace(day=calendar.monthrange(ds.year,ds.month)[1]))]):raise ValidationError('An enrolment cycle already exists for this programme and month.')

class MonthlyDisbursementGuards(models.Model):
    _inherit='g2p.disbursement.cycle'
    nsipa_approval_status=fields.Char(string='List approval',compute='_nsipa_approval_status')
    @api.depends('beneficiary_list_ids.nsipa_status','approved_for_disbursement','program_id.nsipa_flow')
    def _nsipa_approval_status(self):
        labels={'pending':'Pending','processing':'Processing','complete':'Complete','finance':'Awaiting Finance','audit':'Awaiting Audit','ceo':'Awaiting CEO','rejected':'Returned for correction','verified':'Fully verified','error':'Processing failed'}
        for c in self:
            c.nsipa_approval_status=(', '.join(labels.get(l.nsipa_status,'') for l in c.beneficiary_list_ids) or 'List not created') if c.program_id.nsipa_flow else ('Approved' if c.approved_for_disbursement else 'Awaiting approval')
    @api.constrains('program_id','nsipa_enrollment_cycle_id','disbursement_schedule_date')
    def _nsipa_cycle_link(self):
        for c in self.filtered(lambda c:c.program_id.nsipa_flow):
            e=c.nsipa_enrollment_cycle_id
            if not e or e.program_id!=c.program_id or not e.approved_for_enrollment:raise ValidationError('Select an approved enrolment cycle from this programme.')
            if not e.disbursement_start_date<=c.disbursement_schedule_date<=e.disbursement_end_date:raise ValidationError('Schedule date must be inside the monthly disbursement window.')
            if self.search_count([('id','!=',c.id),('program_id','=',c.program_id.id),('nsipa_enrollment_cycle_id','=',e.id)]):raise ValidationError('A disbursement cycle already exists for this monthly enrolment cycle.')

class CashBenefitGuard(models.Model):
    _inherit='g2p.benefit.codes'
    def write(self,vals):
        if {'measurement_unit','benefit_type','decimal_places'} & vals.keys():
            for p in self.env['g2p.program.benefit.codes'].sudo().search([('benefit_code_id','in',self.ids),('program_id.nsipa_flow','=',True)]).mapped('program_id'):
                if p.beneficiary_list_ids:raise UserError('Cash benefit currency, type and precision are locked after list creation.')
            if ('measurement_unit' in vals and str(vals['measurement_unit']).upper()!='NGN') or ('benefit_type' in vals and vals['benefit_type'] not in ['CASH_DIGITAL','CASH_PHYSICAL']):
                if self.env['g2p.program.benefit.codes'].sudo().search_count([('benefit_code_id','in',self.ids),('program_id.nsipa_flow','=',True)]):raise ValidationError('Mapped approval-flow benefits must remain cash in NGN.')
        return super().write(vals)
