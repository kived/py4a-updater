import os
import traceback
import urllib2
from threading import Thread, Event
from time import sleep, time
from jnius import autoclass
from kivy.lib import osc
from pyupdater import SERVICE_PORT, CLIENT_PORT, SERVICE_PATH, MESSAGE_UPDATE_AVAILABLE, MESSAGE_DO_UPDATE, \
	MESSAGE_CHECK_FOR_UPDATE
from pyupdater.util import get_current_version, mContext

Environment = autoclass('android.os.Environment')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
File = autoclass('java.io.File')


class Updater(object):
	def __init__(self, updateurl, frequency=600):
		print 'updater init'
		self.updateurl = updateurl
		self.dlthread = None
		self.dlready = Event()
		self.available_version = None
		self.available_version_number = ''
		self.current_version = None
		self.frequency = frequency
		self.last_check = None
		self.downloadurl = None
		self.downloadfile = None
	
	def get_current_version(self):
		print 'getting current version...'
		version_code = get_current_version()
		print 'current version =', version_code
		return version_code
	
	def run(self):
		print 'updater run'
		osc.init()
		oscid = osc.listen('127.0.0.1', SERVICE_PORT)
		osc.bind(oscid, self.recv_osc, SERVICE_PATH)
		print 'listening for OSC'
		self.current_version = self.get_current_version()
		
		while True:
			if not self.last_check or (self.last_check + self.frequency) < time():
				if self.check_for_update():
					self.download_update()
			
			if self.dlready.is_set():
				self.notify_client()
				self.dlready.clear()
			
			osc.readQueue(oscid)
			
			sleep(.1)
	
	def check_for_update(self):
		try:
			print 'checking for updates at', self.updateurl
			print 'last checked:', str(self.last_check)
			
			response = urllib2.urlopen(self.updateurl)
			version_code, version_number, dlurl = response.read().split(',')
			response.close()
			
			self.available_version = int(version_code)
			self.available_version_number = version_number
			self.downloadurl = dlurl
			
			print 'found version', self.available_version, '(current version %d)' % self.current_version
			return self.available_version > self.current_version
		except Exception:
			print 'check for update failed!'
			traceback.print_exc()
			return False
		finally:
			self.last_check = time()
			print 'update last checked:', str(self.last_check)
	
	def download_update(self):
		if self.dlthread and self.dlthread.is_alive():
			print 'download already in progress!'
			return
		
		print 'starting download in thread'
		self.dlthread = Thread(name='dlthread', target=self._download)
		self.dlthread.run()
	
	def _download(self):
		fd = None
		print 'downloading', self.downloadurl
		self.dlready.clear()
		try:
			response = urllib2.urlopen(self.downloadurl)
			update = response.read()
			response.close()
			
			dlfile = os.path.join(Environment.getExternalStorageDirectory().getPath(), 'py4aupdate.apk')
			with open(dlfile, 'w') as f:
				f.write(update)
			self.downloadfile = dlfile
			print 'download successful'
			self.dlready.set()
		except Exception:
			print 'download failed!'
			traceback.print_exc()
	
	def notify_client(self):
		osc.sendMsg(SERVICE_PATH, [MESSAGE_UPDATE_AVAILABLE, self.available_version, self.available_version_number], port=CLIENT_PORT)
	
	def recv_osc(self, message, *args):
		print 'service osc message:', message, args
		command = message[2]
		if command == MESSAGE_DO_UPDATE:
			self.update()
		elif command == MESSAGE_CHECK_FOR_UPDATE:
			if self.check_for_update():
				self.download_update()
	
	def update(self):
		if not self.available_version:
			print 'no updates found!'
			return
		
		if not self.downloadfile:
			print 'update not downloaded!'
			return
		
		print 'starting update to', self.available_version, 'from', self.downloadfile
		dluri = Uri.fromFile(File(self.downloadfile))
		intent = Intent(Intent.ACTION_VIEW)
		intent.setDataAndType(dluri, 'application/vnd.android.package-archive')
		intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
		mContext().startActivity(intent)
	
