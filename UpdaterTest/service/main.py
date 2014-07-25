'''
Sample Android app updater service.

Remember to set the update check url below.
'''

UPDATE_CHECK_URL = 'http://192.168.2.129/updatecheck.txt'

from pyupdater.service import Updater

print 'service loading'

if __name__ == '__main__':
	print 'service starting'
	Updater(UPDATE_CHECK_URL).run()
