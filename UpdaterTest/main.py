'''
Sample Android app to test auto updates.

Change the update check URL in service/main.py
'''

import kivy
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

kivy.require('1.8.1')

from kivy.app import App
from kivy.lang import Builder

from pyupdater.client import UpdateClient

root = Builder.load_string('''
<UpdaterUI>:
	orientation: 'vertical'
	Label:
		size_hint_y: None
		height: self.texture_size[1]
		text: 'Updater Test App'
	
	BoxLayout:
		Label:
			text: 'Current version'
		Label:
			text: root.current_version
	
	BoxLayout:
		Label:
			text: 'Update available?'
		Label:
			text: 'Yes' if root.update_available else 'No'
	
	BoxLayout:
		Label:
			text: 'Available version'
		Label:
			text: root.available_version
	
	BoxLayout:
		size_hint_y: None
		height: sp(128)
		Button:
			text: 'Check for updates'
			on_press: root.check_updates()
		Button:
			text: 'Apply updates'
			on_press: root.apply_updates()
''')

class UpdaterUI(BoxLayout):
	client = ObjectProperty()
	
	current_version = StringProperty()
	available_version = StringProperty()
	update_available = BooleanProperty(False)

	def __init__(self, **kwargs):
		super(UpdaterUI, self).__init__(**kwargs)
		
		assert isinstance(self.client, UpdateClient)
		if not self.client:
			raise ValueError('no update client provided!')
		
		self.client.bind(update_available=self.setter('update_available'))
		self.client.bind(update_version=self.setter('available_version'))
		
		self.update_available = self.client.update_available
		self.available_version = self.client.update_version
		self.current_version = self.client.current_version

	def check_updates(self):
		self.client.check_for_update()
	
	def apply_updates(self):
		self.client.do_update()

class UpdaterApp(App):
	def build(self):
		print 'start android service'
		from android import AndroidService
		self.service = AndroidService('updater', 'running')
		self.service.start('start')
		return UpdaterUI(client=UpdateClient())
	
	def on_pause(self):
		return True

if __name__ == '__main__':
	UpdaterApp().run()
