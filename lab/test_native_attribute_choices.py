from test_meeting_native_workflow import call
body,status=call('aarin@gmail.com','attributes/values',{'attribute_id':'ROOF_MATERIAL','current_page':1,'page_size':500},False)
print({'status':status,'keys':list(body),'error':body.get('error'),'values':len(body.get('values',[])),'sample':str(body)[:500]})
