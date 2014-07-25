from jnius import autoclass, cast

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
