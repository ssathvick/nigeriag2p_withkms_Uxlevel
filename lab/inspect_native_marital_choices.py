from test_mbr_db_connection import connect
with connect('master_data') as c:
 with c.cursor() as q:q.execute("SELECT value_code,value_display FROM g2p_attribute_values WHERE attribute_id='MARITAL_STATUS' ORDER BY sort_order");print(q.fetchall())
