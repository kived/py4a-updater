from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.lib import osc
from kivy.properties import StringProperty, AliasProperty
from pyupdater import CLIENT_PORT, SERVICE_PORT, MESSAGE_UPDATE_AVAILABLE, MESSAGE_DO_UPDATE, MESSAGE_CHECK_FOR_UPDATE, \
	SERVICE_PATH
from pyupdater.util import get_current_version


class UpdateClient(EventDispatcher):
	update_version = StringProperty('')
	
	def get_update_available(self):
		return bool(self.update_version)
	update_available = AliasProperty(get_update_available, bind=('update_version',))
	
	current_version = StringProperty('')
	
	def __init__(self, **kwargs):
		super(UpdateClient, self).__init__(**kwargs)
		
		osc.init()
		oscid = osc.listen('127.0.0.1', CLIENT_PORT)
		osc.bind(oscid, self.recv_osc, SERVICE_PATH)
		Clock.schedule_interval(lambda _: osc.readQueue(oscid), 0)
		
		self.current_version = str(get_current_version())
	
	def recv_osc(self, message, *args):
		print 'client osc message:', message, args
		command = message[2]
		if command == MESSAGE_UPDATE_AVAILABLE:
			version_number = message[3]
			self.update_version = str(version_number)
	
	def send_osc(self, *message):
		osc.sendMsg(SERVICE_PATH, message, port=SERVICE_PORT)
	
	def do_update(self, *_):
		print 'client: do update'
		if self.update_available:
			self.send_osc(MESSAGE_DO_UPDATE)
	
	def check_for_update(self, *_):
		print 'client: check for updates'
		self.send_osc(MESSAGE_CHECK_FOR_UPDATE)
