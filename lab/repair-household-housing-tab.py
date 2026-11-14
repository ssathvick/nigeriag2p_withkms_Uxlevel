"""Repair the Housing & Services tab links in the Nigeria registry metadata.

Run inside the lab environment with kubectl and psql configured, using python3.
This changes tab-to-section metadata only; household records are untouched.
"""
from labdb import query

SQL = """
BEGIN;
UPDATE g2p_register_ui_tab_sections AS mapping
SET tab_id = 'household_housing_services_tab'
WHERE mapping.register_id = 'a0000000-0000-4000-8000-000000000002'
  AND mapping.tab_id = 'housing_services_tab'
  AND mapping.section_id IN ('hh_dwelling_services', 'hh_table_assets')
  AND EXISTS (
      SELECT 1 FROM g2p_register_ui_tabs AS tab
      WHERE tab.register_id = mapping.register_id
        AND tab.tab_id = 'household_housing_services_tab'
        AND tab.is_active
  )
  AND NOT EXISTS (
      SELECT 1 FROM g2p_register_ui_tab_sections AS existing
      WHERE existing.register_id = mapping.register_id
        AND existing.tab_id = 'household_housing_services_tab'
        AND existing.section_id = mapping.section_id
  );
COMMIT;
SELECT section_id, section_order FROM g2p_register_ui_tab_sections
WHERE register_id = 'a0000000-0000-4000-8000-000000000002'
  AND tab_id = 'household_housing_services_tab'
ORDER BY section_order;
"""

if __name__ == '__main__':
    print(query('register', SQL))
