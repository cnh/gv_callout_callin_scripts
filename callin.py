import os, sys
print 0.5
from freeswitch import  *
print 0.51
os.environ['DJANGO_SETTINGS_MODULE'] = 'testing.testing.settings'
print 0.52
#from models import call_records, callin_records
print 0.53
from datetime import datetime
import traceback
import time


def handler(session, args):
    print 0
    print os.getcwd()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'testing.testing.settings'
    print('\n In callin.py, before answer')
    print ('\n type & dir of session object...type is \t' + str(type(session)) +' \t dir is \t'+ str(dir(session)))
    session.answer()
    '''
    now update the latest entry in the callout_records table with a False in the recvd_callback field to True
    sql
    UPDATE callout_records SET recvd_callback = TRUE WHERE id=max(id) AND recvd_callback=TRUE;
    '''  
    #self.call_out_entry.recvd_callback = TRUE
    msg1 = '\n In callin, after session.answer(), before callout  update \n'
    print msg1
    
    time.sleep(20)
    
    #co_record_to_update = monitoring.call_hbeat.models.callout_records.objects.filter(recvd_callback = False).order_by('-id')[0]
    '''
    if ( call_records.objects.filter(recvd_callback = False ).count() > 0 ):
        cr_to_update = call_records.objects.filter(recvd_callback = False).order_by('-id')[0]
        cr_to_update.recvd_callback = True
        cr_to_update.callback_time = datetime.now()
        cr_to_update.callback_num = session.getVariable("caller_id_number")
        cr_to_update.save()
        msg2 = "Callrecords table entry's id which was updated is " + str(cr_to_update.id)
        print msg2
        msg3 = "Callrecords table entry which was updated's callout time, recvd_callback, email_sent is \t" 
        +  str(cr_to_update.callout_time) +'\t'+cr_to_update.recvd_callback + '\t' + cr_to_update.email_sent 
        print msg3
        msg35 = '\n call records entry\'s callback time & callback num are \t'+cr_to_update.callback_time +'\t'  + cr_to_update.callback_num
        print msg35
    '''
    
    
            
    
    msg4 = '\n In callin, after callout update, before call_in entry save \n'
    print msg4
    
    
    callers_num = session.getVariable("caller_id_number")
    msg5 = '\n In callin, caller id # was ' + callers_num
    print msg5
    
    #call_in_entry = callin_records(caller_num = callers_num,callin_time = timezone.now())
    #call_in_entry.save()
    print os.getcwd()
    try:
        fsock = open('callin.log', 'a+')
        try:
            fsock.write('\n')
            fsock.write('\t' + str(datetime.now()) +'\t' + callers_num + '\t' )
            fsock.write('\n')
            print '\n after file write, in directory'
            print os.getcwd()
        finally:
            fsock.close()
    except IOError as ioe:
        print ('\n Exception occurred, error is ' + str(ioe))
        traceback.print_exc()
        
    
    
    msg6 = '\n In callin, after call_in_entry db entry '
    print msg6
    
    print ("Hanging up after answering callback from " + callers_num)
    session.hangup("Hanging up after answering callback from ")
    
    print( "\n After hangup " )
