from enum import Enum
import time

class Instance_V:
    def __init__(self, **kwargs):
        self.id_contract = kwargs.get("id_contract")
        self.time_created = kwargs.get("time_created")
        self.instance_num = kwargs.get("instance_num")
        self.polling_count = 0
        self.status_msg = None
        self.actual_status = None
        self.status: Status = None
    def get_exec_time(self):
        return (time.time() - self.time_created) / 60
        


class Status(Enum):
    ERROR_1 = "unexpected_fault_address"
    ERROR_2 = "unable_to_find_image"
    ERROR_3 = "loading_stuck"
    RUNNING = "running"
    RUNNING_FAST_EXIT = "running_fast_exit"
    LOADING = "loading"
