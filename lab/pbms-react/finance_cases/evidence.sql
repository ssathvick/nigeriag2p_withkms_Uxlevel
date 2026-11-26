CREATE SCHEMA IF NOT EXISTS pbms_finance;
CREATE OR REPLACE VIEW pbms_finance.instructions AS
SELECT d.id AS instruction, d.disbursement_envelope_id AS envelope,
       d.disbursement_batch_control_id AS batch, d.beneficiary_id,
       d.disbursement_quantity AS issued_amount, d.receipt_time_stamp AS issued_at,
       e.measurement_unit AS currency, x.remittance_statement_id AS remittance,
       x.reversal_statement_id AS reversal
FROM public.disbursements d JOIN public.disbursement_envelopes e ON e.id=d.disbursement_envelope_id
LEFT JOIN public.disbursement_recons x ON x.disbursement_id=d.id;
CREATE OR REPLACE VIEW pbms_finance.entries AS
SELECT (m)[4] AS instruction, s.statement_id AS receipt, s.statement_number AS statement,
       s.statement_process_timestamp AS processed_at, (m)[1] AS movement_date,
       (m)[2] AS direction, replace((m)[3],',','.')::numeric AS amount,
       substring(l.statement_lob from ':60[FM]:[CD][0-9]{6}([A-Z]{3})') AS currency,
       (m)[5] AS bank_ref, b.ordinality AS entry_number
FROM public.account_statements s JOIN public.account_statement_lobs l USING(statement_id)
CROSS JOIN LATERAL regexp_matches(l.statement_lob,
    '(?:^|\n):61:([0-9]{6})(?:[0-9]{4})?(RD|RC|D|C)([0-9]+(?:,[0-9]+)?)N[A-Z0-9]{3}([^/\r\n]+)//([^\r\n]+)', 'g')
    WITH ORDINALITY AS b(m, ordinality)
WHERE s.statement_process_status='PROCESSED';