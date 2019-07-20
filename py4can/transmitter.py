import time


class Transmitter(object):
    """ """

    def __init__(self, store, canbus):
        self._store = store
        self._bus = canbus
        self._can_sending_tasks = {}
        self._init_messages()

    def _init_messages(self):
        for msg in self._store.messages:
            msg.sig.setitem_callback = self._update_sending_value
            self._can_sending_tasks[msg.name] = None

    def _update_sending_value(self, signal_name):
        msg = self._store.msgs_by_signal_name[signal_name]
        current_send_task = self._can_sending_tasks[msg.name]
        if current_send_task:
            # Signal value is updated for 2nd or more time
            if current_send_task.end_time:
                # Signal is transmitted on timed basis
                if current_send_task.end_time > time.time():
                    # Timed singal is being transmitted yet
                    self.send(msg, current_send_task.period*1000, current_send_task.end_time - time.time())
                else:
                    # Timed signal transmission is completed
                    pass
            else:
                # Signal is being transmitted indefinitely
                self.send(msg, current_send_task.period*1000)

    def send(self, msg, period_in_ms=None, duration=None):
        send_task = self._can_sending_tasks[msg.name]
        if send_task:
            send_task.stop()
        # TODO: Move below line to .sig setting place
        msg._update_sig_to_byte()
        try:
            period_in_s = float(period_in_ms)/1000
            send_task = self._bus.send_periodic(msg.can_formatted, period_in_s, duration=duration)
        except TypeError:
            send_task = self._bus.send(msg.can_formatted)
        self._can_sending_tasks[msg.name] = send_task
        return send_task

    def send_msg_once(self, msg_key):
        # return self.send(self.get_message(msg_key))
        raise NotImplementedError

    def suspend_tx(self, duration=0):
        for msg_name, send_task in self._can_sending_tasks.items():
            if send_task:
                send_task.stop()

    def resume_tx(self):
        for msg_name, send_task in self._can_sending_tasks.items():
            if send_task:
                send_task.start()

