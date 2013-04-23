from BaseTemplatrDialog import BaseDialog
import os, sys

class TTIntroDialog(BaseDialog):
	def __init__(self, on_start=None, on_end=None, default_path=None):
		self.server_root_path = default_path

		self.on_start = on_start
		self.on_end = on_end

		super(TTIntroDialog,self).__init__(None)
		self._ui_reset()

	def select_path(self, event):
		print "Got something"
		print event	
		print event.Path

		if not self.server_started:
			self.server_root_path = event.Path

	def start_server(self, event):
		print "Trying to start " + self.server_port.GetValue()
		print "Trying to root at", self.server_root_path

		if self.server_started:
			self._begin_server_stop()
		else:
			try:
				if self.server_root_path and len(self.server_root_path) > 0 and os.path.exists(self.server_root_path):
					if not self._begin_server_start():
						raise
				else:
					raise
			except Exception, e:
				print e
				self._end_server_start(is_success=False,message='Invalid root directory')


	def exit_server(self,event):
		#self.__do_exit();
		self.__do_end()
		sys.exit(-1)


	def _begin_server_start(self):
		self.status_text.SetForegroundColour((0,255,0))
		self.status_text.SetLabelText("Starting Server...")
		self.themes_directory.Disable()
		self.server_ctrl_button.Disable()

		if self.__do_start():
			self._end_server_start(is_success=True)
			return True

		return False




	def _end_server_start(self, is_success=True, server_location='localhost:8080',message='Server Start Failed'):
		if is_success:
			self.status_text.SetForegroundColour((0,255,0))
			self.status_text.SetLabelText("Server running at %s" % server_location)
			self.server_started = True
			self.server_ctrl_button.SetLabelText("Stop Server")

			# Server started - can't modify path or port
			self.server_port.Disable()
			self.themes_directory.Disable()
			self.server_ctrl_button.Enable()

		else:
			self.__do_end()
			self._ui_reset()
			self.status_text.SetForegroundColour((255,0,0))
			self.status_text.SetLabelText(message)


	def _begin_server_stop(self):
		self._ui_reset()
		self.__do_end()

	def _ui_reset(self):
		self.server_started = False
		self.status_text.SetLabelText("")
		self.server_ctrl_button.SetLabelText("Start Server")

		self.server_port.Enable()
		self.themes_directory.Enable()
		self.server_ctrl_button.Enable()

	def __do_start(self):
		if self.on_start and hasattr( self.on_start, '__call__' ):
			params = {
				'port' : self.server_port.GetValue(),
				'path' : self.server_root_path 
			}
			return self.on_start(**params)

		return False

	def __do_end(self):
		if self.on_end and hasattr( self.on_end, '__call__'):
			return self.on_end()

		return False

	def __do_exit(self):
		if self.on_exit and hasattr( self.on_exit, '__call__'):
			return self.on_exit()

		return False		





