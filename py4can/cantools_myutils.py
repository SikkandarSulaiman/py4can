import can
import cantools
from cantools.database.can.database import Database
from cantools.database.can.message import Message
import common_utils

from functools import partial

class MyMessage(Message):
	"""docstring for MyMessage"""
	def __init__(self, std_msg, **kwargs):
		self._std_msg = std_msg
		self._in_file = False
		self._cycle_time = 0
		self._duration = 0
		self._send = True
		self._byte = None
		self._sig = self._gen_tx_dict()
		self._data_encode = lambda msg: msg.encode(msg.sig)
		try:
			std_msg = kwargs['data']
			kwargs['data'] = self._data_encode(std_msg)
		except KeyError:
			pass
		self._partial_can_fmt = partial(can.Message, arbitration_id=std_msg.frame_id, extended_id=False, **kwargs)
		super().__init__(std_msg.frame_id, std_msg.name, std_msg.length, std_msg.signals)

	def _update_sig_to_byte(self):
		self._byte = self._data_encode(self)
		self.can_formatted = self._partial_can_fmt(data=self._byte)

	def _update_byte_to_sig(self):
		#If bytes are represented as string, convert to int -> 'FF' to 255
		bytes_as_int = list(map(lambda x: x if isinstance(x, int) else int(x, base=16), self._byte))
		self._sig = self.decode(bytes_as_int, decode_choices=False)

	@property
	def sig(self):
		return self._sig

	@sig.setter
	def sig(self, new_sig):
		self._sig = common_utils.KeyFrozenDict(new_sig)

	@property
	def byte(self):
		return self._byte

	@byte.setter
	def byte(self, new_data):
		if len(new_data) != self._std_msg.length:
			raise ValueError
		self._byte = common_utils.IndexFrozenList(new_data)
		self._update_byte_to_sig()
	
	def _gen_tx_dict(self, def_val=0):
		data_dic = {}
		for sig in self._std_msg.signals:
			data_dic[sig.name] = def_val
		self._byte = common_utils.IndexFrozenList([def_val for _ in range(self._std_msg.length)])
		return common_utils.KeyFrozenDict(data_dic)



class MyDatabase(Database):
	"""docstring for MyDatabase"""
	def __init__(self, arg):
		super().__init__()
		self.arg = arg

	def get_all_messages(self):
		return self.messages

	def get_message(self, msg_name):
		msg = self.arg.get_message_by_name(msg_name)
		return MyMessage(msg)



def load_dbc(filename):
	dbc_file = cantools.database.load_file(filename,
		database_format=None,
        encoding='utf-8',
        frame_id_mask=None,
        strict=True,
        cache_dir=None)
	return dbc_file
