from celery.task import Task
from celery.task import PeriodicTask
from celery.registry import tasks

from models import *
from vapp.telephony.utils import *
from vapp.telephony.inbound import FreeswitchSession
#from common import *
from django.core.mail import EmailMessage
import re
import sys, subprocess, commands
from datetime import datetime, timedelta

from models import call_records, callin_records

class CalloutTask(Task):
    #run_every = timedelta(minutes = 1)
	
	def get_ipadd_machinename(self):
		'''
		returns ip add. & hostname of machine where this monitoring script runs
		'''
		print 1
		return {'ipadd':commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:] , 
		'hostname':commands.getoutput("/bin/hostname") }
	def call_send_email2(self, sub, body):
		"""
		passes it's arguments( sub & body) to the send_email function on 
		the machine specified by remote_ip
		"""
		#login_string = 'ssh zahirk@106.187.101.30 python send_email.py email_subject email_body'
		monitor_logfile = open('monitor.log', 'a')
		user = 'zahirk'
		remote_ip = '106.187.101.30'
		cmd = 'python send_email2.py "%s" "%s"' % (sub, body)
		before_ssh_msg = '\n' + str(datetime.now()) +' \n Trying to ssh to remote m/c w/ ip '+ remote_ip +' to send email '
		print before_ssh_msg
		monitor_logfile.write(before_ssh_msg)
		#monitor_logfile.write('\n' + str(datetime.now()) +'\n Trying to ssh to remote m/c ' + remote_ip + ' to send email')
		try:
			out = subprocess.check_output(['ssh', '%s@%s' % (user, remote_ip), cmd])
		except subprocess.CalledProcessError as e:
			monitor_logfile.write('\n'+ str(datetime.now())+' \n Error in ssh-ing to ' + remote_ip + ' to send email '+str(e) )
			print >>sys.stderr, str(e)   # handle/log the error, retry
		after_ssh_msg = '\n' + str(datetime.now()) +' \n successfully ssh-ed to remote m/c' +remote_ip + ' & sent email to admins'
		print after_ssh_msg
		monitor_logfile.write(after_ssh_msg)
	
	def get_url_string_dest_num(self, dest_num = '8800097458', ip_add =  '10.76.9.78'):
		'''
		Constructs the url string to make an outgoing call (using FS originate)
		dest_num : destination number , e.g. 88000258585
		ip_add   : ip add. from topex where call is being made, e.g. 10.76.9.78
		'''
		originate_string = '{ignore_early_media=true}sofia/internal/0091'
		originate_string += dest_num +'@'+ ip_add
		return {
				'url' : originate_string,
				'called_num' : dest_num 
				}
				
	def run(self):
		print 0
		try:
			if call_records.objects.filter(recvd_callback = False).filter(email_sent = False).count() > 0:
				ipadd_machinename = self.get_ipadd_machinename()
				e_sub = 'callback not received on '+ipadd_machinename['hostname'] + ' FAILED at ' + str(datetime.now())
				e_body =  'Callback not received from production server'
				e_body += '\n' + str(datetime.now()) +' Callback monitoring script ran on host named \''+ ipadd_machinename['hostname'] +'\' with ip add ' +   ipadd_machinename['ipadd']
				self.call_send_email2(e_sub, e_body)
			
			
			url_string_dest_num = self.get_url_string_dest_num()
			self.url_string = url_string_dest_num['url']
			self.called_num = url_string_dest_num['called_num']
			print('\n FS originate will use url string ' + self.url_string )
			print('\n\n  Before creating FreeswitchSession object to call ' + self.called_num )
			app_instance = vapp.app_manager.models.App_instance.objects.get(pk = 10)# ai_id(app instance id) for mnews is 10, see line24 of app_manager/tasks.py
			session = FreeswitchSession(app_instance)
			session.originate(self.url_string, self.called_num)
			print('\n\n After calling originate on FreeswitchSession object')
			
			print('\n\n before db entry')
			self.cr_entry = call_records(callout_time = datetime.now())
			self.cr_entry.save()
			print('\n\n after db entry')
			#wait/sleep for 30s ?
			if session.getState() != 'CS_HANGUP':
				session.hangup() #as in line 69 of vapp/act_mcd/handler.py
		
		
		except Exception as e:
			error_msg = '\n Error while calling FS originate 1\n' + str(e)
			print error_msg
			#fs_call_logger.write(error_msg)
			sys.exit(error_msg)
	
tasks.register(CalloutTask)		
