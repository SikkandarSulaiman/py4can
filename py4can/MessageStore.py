import cantools_myutils


class MessageStore(object):
	"""serves as a message database, where messages are stored in a format that can be easily
	utilized by the application end. Messages are stored only in Store object and updated always"""

	def __init__(self, dbc_filename):
		self.msgs_by_signal_name = {}          # {signal_name : message_name}
		self.msgs_by_frame_id = {}             # {message_id : cantools.database.can.message}
		self.msgs_by_name = {}                 # {message_name : cantools.database.can.message}
		self.messages = []
		try:
			self._dbc_thing = cantools_myutils.load_dbc(dbc_filename)
		except Exception as e:
			raise e
		self._init_messages()


	def reinitialize(self):
		self._init_messages();


	def _init_messages(self):
		for msg in self._dbc_thing.messages:
			signalled_msg = cantools_myutils.MyMessage(msg)
			self.messages.append(signalled_msg)
			self.msgs_by_frame_id[msg.frame_id] = signalled_msg
			self.msgs_by_name[msg.name] = signalled_msg
			for signal in msg.signals:
				self.msgs_by_signal_name[signal.name] = signalled_msg


