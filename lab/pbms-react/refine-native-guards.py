from pathlib import Path
p=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/nsipa_approval/models.py')
s=p.read_text()
s=s.replace("            admin_program(p)\n            if not p.nsipa_setup_ready", "            admin_program(p)\n            self.env.cr.execute('SELECT id FROM g2p_program_definition WHERE id=%s FOR UPDATE',[p.id])\n            if not p.nsipa_setup_ready",1)
s=s.replace("            admin_program(p)\n            e=self.env['g2p.enrollment.cycle']", "            admin_program(p)\n            self.env.cr.execute('SELECT id FROM g2p_program_definition WHERE id=%s FOR UPDATE',[p.id])\n            e=self.env['g2p.enrollment.cycle']")
s=s.replace("            cycle_field='enrollment_cycle_id' if e else 'disbursement_cycle_id';cycle=e or d\n", "            cycle_field='enrollment_cycle_id' if e else 'disbursement_cycle_id';cycle=e or d\n            self.env.cr.execute('SELECT id FROM '+('g2p_enrollment_cycle' if e else 'g2p_disbursement_cycle')+' WHERE id=%s FOR UPDATE',[cycle.id])\n")
s=s.replace("        self.ensure_one(); admin_program(self)\n        if not self.nsipa_flow", "        self.ensure_one(); admin_program(self)\n        self.env.cr.execute('SELECT id FROM g2p_program_definition WHERE id=%s FOR UPDATE',[self.id])\n        if not self.nsipa_flow")
s=s.replace("            if not p.nsipa_setup_ready:raise UserError('Complete programme setup first.')", "            if p.program_status!='ACTIVE':raise UserError('The programme must be Active before creating a list.')\n            if not p.nsipa_setup_ready:raise UserError('Complete programme setup first.')")
s=s.replace("    def action_open_summary_wizard(self):\n        return super().action_open_summary_wizard()\n",'')
# Native BIFF XLS supports many worksheets; split at the 65,536 row boundary.
old="""        book=xlwt.Workbook();sheet=book.add_sheet('Beneficiaries');headers=['Beneficiary ID','Name','State','Amount NGN','Programme','Disbursement cycle','Revision']
        for col,h in enumerate(headers):sheet.write(0,col,h);sheet.col(col).width=6000
        for i,line in enumerate(self.nsipa_line_ids.filtered('included'),1):
            if i>=65536:raise UserError('This list exceeds the XLS worksheet limit. Split it before export.')
            for j,v in enumerate([line.beneficiary_id,line.name,line.state or '',line.amount,self.program_id.program_mnemonic,self.disbursement_cycle_id.cycle_mnemonic,self.nsipa_revision]):sheet.write(i,j,v)
"""
new="""        book=xlwt.Workbook();headers=['Beneficiary ID','Name','State','Amount NGN','Programme','Disbursement cycle','Revision']
        sheet=None
        for index,line in enumerate(self.nsipa_line_ids.filtered('included')):
            row=index%65535+1
            if row==1:
                sheet=book.add_sheet('Beneficiaries '+str(index//65535+1))
                for col,h in enumerate(headers):sheet.write(0,col,h);sheet.col(col).width=6000
            for j,v in enumerate([line.beneficiary_id,line.name,line.state or '',line.amount,self.program_id.program_mnemonic,self.disbursement_cycle_id.cycle_mnemonic,self.nsipa_revision]):sheet.write(row,j,v)
"""
assert old in s;s=s.replace(old,new)
p.write_text(s)
