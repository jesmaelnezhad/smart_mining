import random

from controller.base_core import BaseCore


class Machine(BaseCore):
    def __init__(self, persistent_interface):
        self.persistent_interface = persistent_interface

    def execute(self):
        print(self.persistent_interface['test'])
        self.persistent_interface['test'] = "test" + str(random.randint(10, 20))
        print("Printing in execute of the machine")

    def get_order_id_to_work_with(self):
        return "order-id-3234-42-4256354-457686-5433-24457869789655-3434w"
