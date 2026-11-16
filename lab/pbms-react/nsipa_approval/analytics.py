"""Read-only, programme-scoped state analytics from native beneficiary list snapshots."""
import re
from collections import defaultdict
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from .models import access_program

# Shared with the existing main-panel boundary catalogue; not inferred from GPS.
STATE_NAMES=['Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara','Federal Capital Territory']
STATE_CODES=['AB','AD','AK','AN','BA','BY','BE','BO','CR','DE','EB','ED','EK','EN','GO','IM','JI','KD','KN','KT','KE','KO','KW','LA','NA','NI','OG','ON','OS','OY','PL','RI','SO','TA','YO','ZA','FC']
def state_name(value):
    key=re.sub(r'[^A-Z0-9]','',str(value or '').upper())
    aliases={re.sub(r'[^A-Z0-9]','',s.upper()):s for s in STATE_NAMES}
    aliases.update(zip(STATE_CODES,STATE_NAMES))
    aliases.update({'NG%02d'%(i+1):s for i,s in enumerate(STATE_NAMES)})
    aliases.update({'NG'+code:s for code,s in zip(STATE_CODES,STATE_NAMES)})
    aliases.update({'FCT':STATE_NAMES[-1],'ABUJA':STATE_NAMES[-1],'ABUJAFEDERALCAPITALTERRITORY':STATE_NAMES[-1]})
    return aliases.get(key)

class ProgrammeGeographicAnalytics(models.Model):
    _inherit='g2p.program.definition'

    @api.model
    def nsipa_analytics_options(self):
        result=[]
        for program in self.search([('nsipa_flow','=',True)],order='program_status,id desc'):
            try:access_program(program)
            except AccessError:continue
            cycles=[]
            for cycle in program.enrollment_cycle_ids:
                cycles.append({'key':'enrollment:%s'%cycle.id,'label':'Enrolment cycle %s · %s'%(cycle.cycle_number,cycle.disbursement_start_date),'stage':'enrollment'})
            for cycle in program.disbursement_cycle_ids:
                cycles.append({'key':'disbursement:%s'%cycle.id,'label':cycle.cycle_mnemonic+' · '+str(cycle.disbursement_schedule_date),'stage':'disbursement'})
            result.append({'id':program.id,'name':program.program_mnemonic,'status':program.program_status,'registry':program.target_registry,'cycles':cycles})
        return result

    def nsipa_geographic_analytics(self,cycle_key):
        self.ensure_one();access_program(self)
        if not self.nsipa_flow:raise UserError('Geographic list snapshots are available for programme approval-flow programmes.')
        if not isinstance(cycle_key,str) or not re.fullmatch(r'(enrollment|disbursement):[1-9][0-9]*',cycle_key):raise ValidationError('Select a valid programme cycle.')
        stage,number=cycle_key.split(':');cycle=self.env['g2p.%s.cycle'%stage].browse(int(number)).exists()
        if not cycle:raise ValidationError('The selected cycle is unavailable.')
        cycle.check_access_rights('read');cycle.check_access_rule('read')
        if cycle.program_id!=self:raise AccessError('The cycle does not belong to this programme.')
        listings=self.env['g2p.beneficiary.list'].search([(stage+'_cycle_id','=',cycle.id),('program_id','=',self.id)])
        rows=defaultdict(lambda:{'beneficiaries':0,'entitlement_ngn':0,'approved_beneficiaries':0,'payment_submitted_beneficiaries':0})
        excluded=0;pending=0
        for listing in listings:
            if listing.nsipa_status in ['pending','processing','error']:
                pending+=1;continue
            for line in listing.nsipa_line_ids:
                if not line.included:excluded+=1;continue
                state=state_name(line.state) or 'Unmapped location'
                row=rows[state];row['beneficiaries']+=1
                row['entitlement_ngn']+=line.amount if stage=='disbursement' else 0
                row['approved_beneficiaries']+=int(listing.nsipa_status=='verified' if stage=='disbursement' else listing.nsipa_status=='complete')
                row['payment_submitted_beneficiaries']+=int(bool(listing.nsipa_payment_hash))
        states=[dict(name=name,**value) for name,value in sorted(rows.items())]
        total=sum(row['beneficiaries'] for row in states);unknown=rows.get('Unmapped location',{}).get('beneficiaries',0)
        return {'program_id':self.id,'programme':self.program_mnemonic,'cycle_key':cycle_key,'stage':stage,'states':states,'total_beneficiaries':total,'mapped_beneficiaries':total-unknown,'unmapped_beneficiaries':unknown,'excluded_beneficiaries':excluded,'entitlement_ngn':sum(row['entitlement_ngn'] for row in states),'pending_lists':pending,'list_count':len(listings),'updated_at':fields.Datetime.to_string(fields.Datetime.now()),'source':'Included beneficiaries in the selected cycle list snapshot. Payment submission is not confirmed settlement.'}
