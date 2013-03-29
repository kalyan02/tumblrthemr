import wx
from dialog.TTIntroDialog import TTIntroDialog
import subprocess, os, signal, webbrowser, time

srv_proc = None

server_script_name = 'server.py' #Default

def set_server(server_name):
	global server_script_name
	server_script_name = server_name


def on_start( path, port ):
	global srv_proc
	if not srv_proc:
		print "PROC START"
		# TODO: Is there a better way ?
		srv_proc = subprocess.Popen(['python',server_script_name,'--path',path,'--port',port,'--mode','server'])
		time.sleep(2)
		webbrowser.open( 'http://localhost:%s' % port )
		return True

	return False

def on_end():
	global srv_proc
	if srv_proc:
		print "PROC END"
		os.kill(srv_proc.pid, signal.SIGINT)
		srv_proc = None

def start():
	# Create a dialog and setup event handlers
	app = wx.App()
	dialog = TTIntroDialog( on_start = on_start, on_end = on_end )
	dialog.Show()
	app.MainLoop()