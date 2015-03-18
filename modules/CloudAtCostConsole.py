# CloudAtCostConsole Copyright (C) 2015 foospidy
# https://github.com/foospidy/CACConsole
# See LICENSE for details
# Cloud At Cost Console

import os
import time
from twisted.internet import stdio, reactor
from twisted.protocols import basic
from twisted.python import log
import sqlite3 as lite
import CACPy # https://github.com/adc4392/python-cloudatcost

class CloudAtCostConsole(basic.LineReceiver):
	from os import linesep as delimiter

	def __init__(self, dbfile):
		self.dbfile = dbfile
		self.db     = lite.connect(self.dbfile)
		self.cursor = self.db.cursor()
		self.using  = []
		self.cac    = None
		
		self.cursor.execute('CREATE TABLE IF NOT EXISTS accounts ( account VARCHAR(200) NOT NULL, apikey VARCHAR(200) NOT NULL );') 

	def connectionMade(self):
		self.do_banner()
		self.sendLine('For help type \'help\'.')
		self.transport.write('CaC>')
	
	def lineReceived(self, line):
		if not line:
			self.transport.write('CaC>')
			return

		# Parse command
		commandParts = line.split()
		command      = commandParts[0].lower()
		args         = commandParts[1:]

		try:
			method = getattr(self, 'do_' + command)
		except AttributeError, e:
			self.sendLine('Error: no such command.')
		else:
			try:
				method(*args)
			except Exception, e:
				self.sendLine('Error: ' + str(e))
		
		self.transport.write('CaC>')

	def do_help(self, command=None):
		"""help [command]: List commands, or show help on the given command"""
		if command:
			self.sendLine(getattr(self, 'do_' + command).__doc__)
		else:
			commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
			self.sendLine("Valid commands:\n\t" +"\n\t".join(commands))
			self.sendLine('Type "help [command]" for more info.')

	### utilities ####################
	
	def do_ping(self, serverid):
		"""ping: Ping a server. Usage: ping [<serverid>|all] """
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		servers = self.cac.get_server_info()

		for i in range(0, len(servers)):
			server_data = servers[i]
			sid         = server_data['sid'].encode('UTF-8')
			ip          = server_data['ip'].encode('UTF-8')
			
			if 'all' == serverid:
				response = os.system('ping -c 3 ' + ip)
			elif serverid == sid:
				response = os.system('ping -c 3 ' + ip)

	def do_usage(self):
		"""usage: Show server(s) utilization"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		servers = self.cac.get_server_info()

		self.sendLine('---------------------------------------------------------------------------------------------------------------------')
		#self.sendLine('sid   hostname    label   template  CPUs  RAM  Disk  Status')
		self.sendLine('{0:11} {1:32} {2:15} {3:4} {4:18} {5:18} {6:10}'.format('SID', 'Hostname', 'Label', 'CPUs', 'RAM', 'Storage', 'Status'))
		self.sendLine('---------------------------------------------------------------------------------------------------------------------')

		for i in range(0, len(servers)):
			server_data = servers[i]
			
			try:
				sid         = server_data['sid'].encode('UTF-8')
				if server_data['lable'] is not None:
					label       = server_data['lable'].encode('UTF-8') # spelling error "lable" in cac api
				hostname    = server_data['hostname'].encode('UTF-8')
				template    = server_data['template'].encode('UTF-8')
				cpu         = server_data['cpu'].encode('UTF-8')
				cpuusage    = server_data['cpuusage'].encode('UTF-8')
				ram         = server_data['ram'].encode('UTF-8')
				ramusage    = round(float(server_data['ramusage']) / int(server_data['ram']) * 100, 2)
				storage     = server_data['storage'].encode('UTF-8')
				hdusage     = round(float(server_data['hdusage']) / int(server_data['storage']) * 100, 2)
				status      = server_data['status'].encode('UTF-8')
		
				self.sendLine('{0:11} {1:32} {2:15} {3:4} {4:18} {5:18} {6:10}'.format(sid, hostname, label, cpu, str(ramusage) + '% of ' + ram, str(hdusage) + '% of ' + storage, status))
			except Exception as e:
				self.sendLine('Error reading host information, perhaps server is re-imaging?')
	
	def do_bash(self):
		"""bash: Drop to bash shell. Type 'exit' to return to CACConsole"""
		response = os.system('/bin/bash')

	### power ####################
	
	def do_poweron(self, serverid):
		"""poweron: Power on a server or all servers. Usage: poweron [<serverid>|all]"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		if 'all' == serverid:
			_poweron_all()
		else:
			power  = self.cac.power_on_server(serverid)
			status = power['status'].encode('UTF-8')
			
			if 'ok' == status:
				action = power['action'].encode('UTF-8')
				taskid = power['taskid']
				result = power['result'].encode('UTF-8')
				
				log.msg('Server poweron. sid ' + serverid)
				self.sendLine(action + ': ' + result + '(taskid: ' + str(taskid) + ')')
				
			else:
				error_description = power['error_description'].encode('UTF-8')
				
				self.sendLine(status + ': ' + error_description)
	
	def _poweron_all(self):
		"""_poweron_all: Power on all servers."""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		servers = self.cac.get_server_info()

		for i in range(0, len(servers)):
			server_data = servers[i]
			serverid    = server_data['sid'].encode('UTF-8')

			power  = self.cac.power_on_server(serverid)
			status = power['status'].encode('UTF-8')
		
			if 'ok' == status:
				action = power['action'].encode('UTF-8')
				taskid = power['taskid']
				result = power['result'].encode('UTF-8')
			
				log.msg('Server poweron. sid ' + serverid)
				self.sendLine(action + ': ' + result + '(taskid: ' + str(taskid) + ')')
				time.sleep(1) # give CaC API a break before continuing
			
			else:
				error_description = power['error_description'].encode('UTF-8')
				
				self.sendLine(status + ': ' + error_description)
		
	def do_poweroff(self, serverid):
		"""poweroff: Power off a server or all servers. Usage: poweroff [<serverid>|all]"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		if 'all' == serverid:
			_poweroff_all()
		else:
			power  = self.cac.power_off_server(serverid)
			status = power['status'].encode('UTF-8')
			
			if 'ok' == status:
				action = power['action'].encode('UTF-8')
				taskid = power['taskid']
				result = power['result'].encode('UTF-8')
				
				log.msg('Server poweroff. sid ' + serverid)
				self.sendLine(action + ': ' + result + '(taskid: ' + str(taskid) + ')')
				
			else:
				error_description = power['error_description'].encode('UTF-8')
				
				self.sendLine(status + ': ' + error_description)
	
	def _poweroff_all(self):
		"""_poweroff_all: Power off all servers."""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
	
		servers = self.cac.get_server_info()

		for i in range(0, len(servers)):
			server_data = servers[i]
			serverid    = server_data['sid'].encode('UTF-8')

			power  = self.cac.power_off_server(serverid)
			status = power['status'].encode('UTF-8')
	
			if 'ok' == status:
				action = power['action'].encode('UTF-8')
				taskid = power['taskid']
				result = power['result'].encode('UTF-8')
		
				log.msg('Server poweroff. sid ' + serverid)
				self.sendLine(action + ': ' + result + '(taskid: ' + str(taskid) + ')')
				time.sleep(1) # give CaC API a break before continuing
		
			else:
				error_description = power['error_description'].encode('UTF-8')
			
				self.sendLine(status + ': ' + error_description)
	
	def do_reset(self, serverid):
		"""reset: Restart a server or all servers. Usage: reset [<serverid>|all]"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
	
		if 'all' == serverid:
			_reset_all()
		else:
			power  = self.cac.reset_server(serverid)
			status = power['status'].encode('UTF-8')
			
			if 'ok' == status:
				action = power['action'].encode('UTF-8')
				taskid = power['taskid']
				result = power['result'].encode('UTF-8')
				
				log.msg('Server reset. sid ' + serverid)
				self.sendLine(action + ': ' + result + '(taskid: ' + str(taskid) + ')')
				
			else:
				error_description = power['error_description'].encode('UTF-8')
				
				self.sendLine(status + ': ' + error_description)
	
	def _reset_all(self):
		"""_reset_all: Restart all servers."""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
	
		servers = self.cac.get_server_info()

		for i in range(0, len(servers)):
			server_data = servers[i]
			serverid    = server_data['sid'].encode('UTF-8')

			power  = self.cac.reset_server(serverid)
			status = power['status'].encode('UTF-8')
	
			if 'ok' == status:
				action = power['action'].encode('UTF-8')
				taskid = power['taskid']
				result = power['result'].encode('UTF-8')
		
				log.msg('Server reset. sid ' + serverid)
				self.sendLine(action + ': ' + result + '(taskid: ' + str(taskid) + ')')
				time.sleep(1) # give CaC API a break before continuing
		
			else:
				error_description = power['error_description'].encode('UTF-8')
			
				self.sendLine(status + ': ' + error_description)
	
	### List ####################

	def do_list(self, list='servers'):
			"""list: List information. Usage: list [accounts|servers|tasks|templates]"""
			if 'accounts' == list:
				self._list_accounts()
			elif 'tasks' == list:
				self._list_tasks()
			elif 'templates' == list:
				self._list_templates()
			else:
				self._list_servers()

	def _list_tasks(self):
		"""_list_tasks: List all tasks in operation"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		tasks = self.cac.get_task_info()
		
		if 0 == len(tasks):
			self.sendLine('No current tasks')

		for i in range(0, len(tasks)):
			task_data = tasks[i]
			serverid  = task_data['serverid'].encode('UTF-8')
			action    = task_data['action'].encode('UTF-8')
			status    = task_data['status'].encode('UTF-8')

			self.sendLine(serverid + '\t' + action + '\t' + status)

	def _list_templates(self):
		"""_list_templates: List all templates available"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		templates = self.cac.get_template_info()

		for i in range(0, len(templates)):
			template_data = templates[i]
			id           = template_data['id'].encode('UTF-8')
			detail       = template_data['detail'].encode('UTF-8')

			self.sendLine(id + '\t' + detail)

	def _list_servers(self):
		"""_list_servers: List all servers on the account"""
		if not self.using:
			self.sendLine('No account selected! Type: help use')
			return
		
		servers = self.cac.get_server_info()

		self.sendLine('---------------------------------------------------------------------------------------------------------------------')
		self.sendLine('{0:11} {1:32} {2:15} {3:15} {4:5} {5:6} {6:7} {7:10}'.format('SID', 'Hostname', 'Label', 'ip', 'CPUs', 'RAM', 'Storage', 'Status'))
		self.sendLine('---------------------------------------------------------------------------------------------------------------------')
		
		for i in range(0, len(servers)):
			server_data = servers[i]
			
			try:
				sid         = server_data['sid'].encode('UTF-8')
				hostname    = server_data['hostname'].encode('UTF-8')
				if server_data['lable'] is not None:
					label       = server_data['lable'].encode('UTF-8') # spelling error "lable" in cac api
				ip          = server_data['ip'].encode('UTF-8')
				template    = server_data['template'].encode('UTF-8')
				cpu         = server_data['cpu'].encode('UTF-8')
				ram         = server_data['ram'].encode('UTF-8')
				storage     = server_data['storage'].encode('UTF-8')
				status      = server_data['status'].encode('UTF-8')
			
				self.sendLine('{0:11} {1:32} {2:15} {3:15} {4:5} {5:6} {6:7} {7:10}'.format(sid, hostname, label, ip, cpu, ram, storage, status))
			except Exception as e:
				self.sendLine('Error reading host information, perhaps server is re-imaging?')
			
	### account ####################
	
	def do_whoami(self):
		"""whoami: Display current account being used for queries"""
		if self.using:
			self.sendLine('You are currently ' + self.using[0].encode('UTF-8'))
		else:
			self.sendLine('You are currently nobody. Cheer up, you\'ll be somebody someday.')

	def do_use(self, email):
		"""use: Select an account to use for API calls. Usage: use <account>"""
		params = [email]
		self.cursor.execute("SELECT account, apikey FROM accounts WHERE account=?", params)
		
		rows = self.cursor.fetchall()
		
		if 0 == len(rows):
			self.sendLine('No account found for ' + email)
		else:
			for row in rows:
				self.using = [row[0], row[1]]
				self.cac   = CACPy.CACPy(self.using[0], self.using[1])
			
			log.msg('Changed account ' + email)
			self.sendLine('Now using ' + email)

	def do_del_account(self, email):
		"""del_account: delete an account. Example: del_account example@example.com"""
		# todo: check if account exist first
		params = [email]
		self.cursor.execute("DELETE FROM accounts WHERE account=?", params)
		self.db.commit()
		
		if self.using:
			if email == self.using[0]:
				self.using = []
		
		log.msg('Deleted account for ' + email)
		self.sendLine('Deleted! I hope you were sure because this cannot be undone.')
		
	def do_add_account(self, email, apikey):
		"""add_account: """
		self.sendLine('Adding entry for ' + email + ' with apikey ' + apikey)
		params = [email, apikey]
		self.cursor.execute("INSERT INTO accounts VALUES (?, ?)", params)
		self.db.commit()
		log.msg('Added account for ' + email)
		self.sendLine('Done!')
	
	def _list_accounts(self):
		"""list_accounts: List all configured services"""
		self.cursor.execute("SELECT account FROM accounts;")
		
		rows = self.cursor.fetchall()
		i    = 0
		
		for row in rows:
			i = i + 1
			self.sendLine(str(i) + '.\t' + row[0].encode('utf-8'))

	def do_banner(self):
		"""banner: Display CloudAtCostConsole banner"""
		banner  = 'ICAgX19fX18gXyAgICAgICAgICAgICAgICAgXyAgICAgICAgIF8gICAgICBfX19fXyAgICAgICAgICBfICAgCiAgLyBfX19ffCB8ICAgICAgICAgICAgICAgfCB8ICAgICAgIHwgfCAgICAvIF9fX198ICAgICAgICB8IHwgIAogfCB8ICAgIHwgfCBfX18gIF8gICBfICBfX3wgfCAgIF9fIF98IHxfICB8IHwgICAgIF9fXyAgX19ffCB8XyAKIHwgfCAgICB8IHwvIF8gXHwgfCB8IHwvIF9gIHwgIC8gX2AgfCBfX3wgfCB8ICAgIC8gXyBcLyBfX3wgX198CiB8IHxfX19ffCB8IChfKSB8IHxffCB8IChffCB8IHwgKF98IHwgfF8gIHwgfF9fX3wgKF8pIFxfXyBcIHxfIAogIFxfX19fX3xffFxfX18vIFxfXyxffFxfXyxffCAgXF9fLF98XF9ffCAgXF9fX19fXF9fXy98X19fL1xfX3wKICAgX19fX18gICAgX19fXyAgICBfICAgXyAgICBfX19fXyAgICBfX19fICAgIF8gICAgICAgIF9fX19fXyAgCiAgLyBfX19ffCAgLyBfXyBcICB8IFwgfCB8ICAvIF9fX198ICAvIF9fIFwgIHwgfCAgICAgIHwgIF9fX198IAogfCB8ICAgICAgfCB8ICB8IHwgfCAgXHwgfCB8IChfX18gICB8IHwgIHwgfCB8IHwgICAgICB8IHxfXyAgICAKIHwgfCAgICAgIHwgfCAgfCB8IHwgLiBgIHwgIFxfX18gXCAgfCB8ICB8IHwgfCB8ICAgICAgfCAgX198ICAgCiB8IHxfX19fICB8IHxfX3wgfCB8IHxcICB8ICBfX19fKSB8IHwgfF9ffCB8IHwgfF9fX18gIHwgfF9fX18gIAogIFxfX19fX3wgIFxfX19fLyAgfF98IFxffCB8X19fX18vICAgXF9fX18vICB8X19fX19ffCB8X19fX19ffCAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIA=='
		
		self.sendLine(banner.decode("base64"))
		self.sendLine('CloudAtCostConsole Copytright (c) 2015 foospidy')
		self.sendLine('Don\'t forget to whitelist your IP address in your CaC panel settings.\n')
	
	def do_quit(self):
		"""quit: Quit CloudAtCostConsole"""
		log.msg('Quiters gonna quit!')
		self.sendLine('Goodbye.')
		self.transport.loseConnection()

	def connectionLost(self, reason):
		# stop the reactor
		log.msg('Connection lost! Shutting down reactor.')
		reactor.stop()
