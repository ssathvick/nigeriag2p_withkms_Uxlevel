from test_mbr_db_connection import connect
with connect() as c:
 with c.cursor() as q:q.execute("UPDATE g2p_register_sections SET section_description='Additional asset records' WHERE section_id='hh_table_assets'")
 c.commit()
