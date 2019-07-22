import os
import sys
import can
import json
import inspect
from pathlib import Path

import py4can
from py4can.common_utils import exec_in_path


class CanBus(object):
    """docstring for CanBus"""

    def __init__(self, config_file, enable_canbus=True):
        self._store = None
        self._bus = None
        self._config_file = config_file
        self._rx_log_file = None
        self._enable_bus = enable_canbus
        try:
            caller_path = str(Path(inspect.stack()[1].filename))
            exec_in_path(self._get_from_file, caller_path.rsplit(os.sep, maxsplit=1)[0])
        except Exception as e:
            raise e

    def _get_from_file(self):
        try:
            with open(self._config_file, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f'Error in config file {self._config_file}', file=sys.stdout)
            raise e
        dbc_file = Path(self._config['dbc_folder_path']) / self._config['dbc_file_name']
        self._store = py4can.MessageStore(dbc_file)
        self._bus = can.interface.Bus(**self._config['bus_parameters']) if self._enable_bus else None

    def get_message(self, msg_key):
        if type(msg_key) == int:
            return self._store.msgs_by_frame_id[msg_key]
        elif type(msg_key) == str:
            if msg_key.startswith('0x'):
                return self._store.msgs_by_frame_id[int(msg_key, base=16)]
            else:
                return self._store.msgs_by_name[msg_key]
        else:
            raise TypeError('Expected msg_id or msg_name')

    def __del__(self):
        try:
            self._bus.shutdown()
        except AttributeError:
            pass
        if self._rx_log_file:
            self._rx_log_file.close()
