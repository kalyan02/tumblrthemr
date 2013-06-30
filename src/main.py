import sys
import argparse
from glob import glob
from multiprocessing import Process, Pipe, Queue
from dialog.TTIntroDialog import TTIntroDialog
import wx
import time
import webbrowser

import server
import conf

print "ARGS", __file__

gui_proc = Process()
srv_proc = None

path = None

def start_server():
	#server.init( args )
	server.start()
	pass

def on_start( path, port ):
	global srv_proc
	#print "ON_START(%s:%s)" % (path,port)
	if path:
		#print "ON_START -> TRYING -> %s" % path
		try:
			srv_proc = Process( target=server.start,args=(path,port) )
			srv_proc.start()
			time.sleep(1)
			webbrowser.open( "http://localhost:%s" %(port) )
		except Exception, e:
			print e.message

		return True
	print "ON_START -> :("
	return False

def on_end():
	global srv_proc
	if srv_proc:
		print "ON_END -> trying"
		srv_proc.terminate()
		srv_proc = None
		return True

def gui_start():
	app = wx.App()
	dialog = TTIntroDialog( on_start = on_start, on_end = on_end )
	dialog.set_build_info(conf.build_version)
	print 'showing dialog'
	dialog.Show()
	app.MainLoop()


gui_start()

#sys.argv.extend(['--path','/Users/kalyan/Dropbox/Projects/Labs/tumblrtemplatr/projects'])
