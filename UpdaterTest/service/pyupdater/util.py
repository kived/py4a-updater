import os
from jnius import autoclass, cast
import subprocess

PythonActivity = autoclass('org.renpy.android.PythonActivity')
PythonService = autoclass('org.renpy.android.PythonService')

def mContext():
	if PythonActivity.mActivity:
		return cast('android.content.Context', PythonActivity.mActivity.getApplication())
	return cast('android.content.Context', PythonService.mService.getApplication())

def get_current_version():
	print 'get_current_version called'
	context = mContext()
	package_name = context.getPackageName()
	print 'package name', package_name
	version_code = context.getPackageManager().getPackageInfo(package_name, 0).versionCode
	return version_code

def check_for_root():
	print 'checking for root access'
	
	su_files = ['/sbin/su', '/system/bin/su', '/system/xbin/su', '/data/local/xbin/su',
	            '/data/local/bin/su', '/system/sd/xbin/su', '/system/bin/failsafe/su',
	            '/data/local/su']
	su = None
	
	for fn in su_files:
		if os.path.exists(fn):
			try:
				cmd = [fn, '-c', 'id']
				output = subprocess.check_output(cmd)
			except Exception:
				pass
			else:
				if 'uid=0' in output:
					su = fn
					print 'root found at', su
					break
	else:
		print 'root not available!'
	
	return su
