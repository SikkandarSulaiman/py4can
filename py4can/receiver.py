import re
from collections import namedtuple

import can


class Receiver(object):
    """ """

    def __init__(self, store, canbus, callbacks={}):
        self._store = store
        self._bus = canbus
        self._rx_data = namedtuple('ReceivedData',
                                   ('timestamp', 'channel', 'msg_name', 'frame_id', 'dlc', 'raw_data', 'signals'))
        self._notifier = None
        self._callback_lut = callbacks
        self._callback_fn = self._launch_callback
        self.enable_rx()

    def enable_rx(self):
        self._notifier = can.Notifier(self._bus, [self._receiver_hub])

    def disable_rx(self):
        self._notifier.stop()

    def enable_callbacks(self):
        self._callback_fn = self._launch_callback

    def disable_callbacks(self):
        self._callback_fn = None

    def register_callback(self, msg_name, function):
        # msg = self._store.msgs_by_name[msg_name]
        self._callback_lut[msg_name] = function

    def _launch_callback(self, msg, rx_data):
        try:
            self._callback_lut[msg.name](rx_data)
        except KeyError:
            pass

    def _receiver_hub(self, recv_data):
        rx_parser = {
            'pattern': r'^Timestamp:\s+([0-9]+\.[0-9]+)\s+ID:\s+([0-9a-fA-F]+)\s+.\s+'
                       r'DLC:\s+([0-9].)\s+(([0-9a-fA-F]{,2}\s){4,8})\s+Channel:\s+([0-9]+)$',
            'timestamp': 1,
            'frame_id': 2,
            'dlc': 3,
            'raw_data': 4,
            'channel': 5
        }
        match = re.search(rx_parser['pattern'], str(recv_data))
        stamp = match.group(rx_parser['timestamp'])
        msg_id = match.group(rx_parser['frame_id'])
        raw_data = match.group(rx_parser['raw_data'])
        channel = match.group(rx_parser['channel'])
        dlc = match.group(rx_parser['dlc'])
        msg = self._store.msgs_by_frame_id[int(msg_id, base=16)]
        msg.byte = raw_data.split()
        self._launch_callback(msg, self._rx_data(stamp, channel, msg.name, msg_id, dlc, raw_data, msg.sig))
        # rx_signals = msg.decode(raw_data.encode(), decode_choices=False)
        # print(f'Channel: {self._config["channel_name"]}')
        # print(f'Timestamp: {stamp}')
        # print(f'Message name: {msg.name}')
        # print(f'Message ID: {msg_id}')
        # pprint(rx_signals)
        # print(50 * '-' + '\n\n')
