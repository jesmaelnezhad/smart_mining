# from data_bank import mine_database as mine_db
# from configuration import EXECUTION_CONFIGS
# from utility.datetime_helpers import datetime_string_to_timestamp
# from utility.datetime_helpers import size_in_seconds
#
# # average_block_count = AverageWindowBlockCount(size_in_seconds(days=1),
# #                                               size_in_seconds(days=30))
# # average_block_count.set_latest_timestamp(datetime_string_to_timestamp('04/01/2020-0:0:0'))
# # # average_block_count.calculate_new_window_values_and_boundaries()
# # average_block_count.update_window_values()
# # values = average_block_count.get_window_values()
# # # print(values)
#
# print(datetime_string_to_timestamp('01/01/2015-0:0:0'))
#
# # user = EXECUTION_CONFIGS.db_user
# # password = EXECUTION_CONFIGS.db_password
# # mine_db_handler = mine_db.MineDatabaseHandler(user, password)
# # begin_timestamp = datetime_string_to_timestamp('04/05/2020-00:00:00')
# # end_timestamp = datetime_string_to_timestamp('04/08/2020-00:00:00')
# # blocks = mine_db_handler.get_blocks_between(begin_timestamp, end_timestamp)
# # print(len(blocks))
#
#
# from datetime import datetime
#
# import pytz
#
# from utility.datetime_helpers import datetime_string_to_timestamp
#
# output_file = open('/home/jamshid/PycharmProjects/smart-miner/files/tmp/blocks.05.01.2021-12.01.2021.mine.csv', 'w')
# output_file.write("moment,id,pool_id\n");
# with open('/home/jamshid/PycharmProjects/smart-miner/files/tmp/blocks.mine.csv.raw') as f:
#     lines = f.readlines()
#     for l in lines:
#         parts = l.split(',')
#         date_str = parts[0]
#         time_str = parts[1]
#         block_id = parts[6]
#         timestamp = int(datetime_string_to_timestamp(datetime_string="{0}-{1}".format(date_str, time_str),
#                                      datetime_format="%d.%m.%Y-%H:%M"))
#         output_file.write("'{0}'".format(datetime.fromtimestamp(timestamp, tz=pytz.UTC)) + "," + block_id + ",1\n")
#
# output_file.close()

# import threading, Condition
#
#
# def driver():
#     spawn_thread::controller(event)
#     # finds out ke yedoone block hal shode
#     # block information ham darim
#     # producer
#
#
#
#
# def controller():
#
#
#
#
#
# def start():
#
#
# def execute():
#
#
# def end():
#
#
#
# from datetime import datetime
#
# DAY_SECONDS = 60 * 60 * 24
# BLOCKS_LIST = None
#
#
# def get_days_delta(smaller, bigger):
#     delta = BLOCKS_LIST[smaller][0] - BLOCKS_LIST[bigger][0]
#     return delta.total_seconds() / DAY_SECONDS
#
#
# def calculate_expected_block_count_per_day(for_index):
#     """
#     Calculates expected block count using the last 500 blocks for the given index
#     :param for_index:
#     :return:
#     """
#     window_size_for_block_count_avg = 500
#     window_days_count_for_avg = get_days_delta(for_index, min(len(BLOCKS_LIST)-1, for_index + window_size_for_block_count_avg))
#     return window_size_for_block_count_avg / window_days_count_for_avg
#
#
# def calculate_x_days_lucky(X):
#     results = []
#     for i, b in enumerate(BLOCKS_LIST[:-500]):
#         # gather latest blocks that fit in X days
#         start = i
#         end = i
#         while end < len(BLOCKS_LIST):
#             days_delta = get_days_delta(start, end)
#             if days_delta > X:
#                 break
#             end += 1
#         x_days_block_count = end - start
#         expected_block_count_per_day = calculate_expected_block_count_per_day(i)
#         results.append(x_days_block_count * 1.0 / (expected_block_count_per_day * X))
#     return results
#
#
# def calculate_x_blocks_lucky(X):
#     results = []
#     for i, b in enumerate(BLOCKS_LIST[:-500]):
#         # average lucks
#         luck_sum = 0
#         for j in range(i, i+X):
#             luck_sum += BLOCKS_LIST[j][1]
#         results.append(luck_sum / X)
#     return results
#
#
# if __name__ == "__main__":
#     blocks_list = []
#     with open('/home/jamshid/PycharmProjects/smart-miner/files/tmp/block_lucks.csv', 'r') as lucks_file:
#         lines = lucks_file.readlines()
#         for l in lines:
#             parts = l.split('\controller')
#             date_time_str = parts[0]
#             block_datetime = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")
#             block_luck = float(parts[1].strip()[:-2])
#             blocks_list.append([block_datetime,block_luck,])
#     BLOCKS_LIST = blocks_list
#     # Generate X-day lucky
#     MAX_X = 30
#     for X in range(1, MAX_X + 1):
#         x_days_lucky = calculate_x_days_lucky(X)
#         for i, l in enumerate(x_days_lucky):
#             BLOCKS_LIST[i].append(l)
#     # Generate X blocks lucky
#     for X in [5, 10, 20, 30, 50, 100, 200, 500]:
#         x_blocks_lucky = calculate_x_blocks_lucky(X)
#         for i, b in enumerate(x_blocks_lucky):
#             BLOCKS_LIST[i].append(b)
#     with open('/home/jamshid/PycharmProjects/smart-miner/files/tmp/block_lucks_generated.csv', 'w') as output_file:
#         for b in BLOCKS_LIST[:-500]:
#             output_file.write("{0}\controller{1}\n".format(b[0], "\controller".join([str(l) for l in b[2 + MAX_X:]])))
#
#
from threading import Thread, Condition, Event, Barrier
from time import sleep

from utility.containers import ThreadSafeDictionary
from utility.events import OrEvent, OrEventPair


class Consumer:
    def __init__(self, name, sleep_time):
        self.message_box = ThreadSafeDictionary()
        self.message_box_changed = Condition()
        self.name = name
        self.sleep_time = sleep_time

    def add_to_message_box(self, key, value):
        self.message_box.set(key, value)
        try:
            self.message_box_changed.acquire()
            self.message_box_changed.notify_all()
        finally:
            self.message_box_changed.release()

    def run(self):
        should_stop = False
        while not should_stop:
            try:
                self.message_box_changed.acquire()
                self.message_box_changed.wait(self.sleep_time)
                self.wake_up()
            finally:
                self.message_box_changed.release()

    def wake_up(self):
        messages = self.message_box.snapshot(should_clear=True)
        print("Consumer {0} woke up.".format(self.name))
        print("Messages are:")
        for k, v in messages.items():
            print("{0}/{1}".format(k, v))


#
# def scheduler(or_event, barrier):
#     while True:
#         or_event.wait(timeout=10)
#         barrier.wait()
#         print("Scheduler")
#
#
# def controller(or_event, barrier):
#     while True:
#         or_event.wait(timeout=10)
#         barrier.wait()
#         print("Controller")
#
#
# def time_tick(period, event, barrier):
#     while True:
#         sleep(period)
#         event.set()
#         barrier.wait()
#         event.clear()
#         print("Time tick")
#
#
# def new_block(id, event, barrier):
#     while True:
#         a = ""
#         while not ("@" in a or id in a):
#             a = input("Enter new input:")
#         event.set()
#         barrier.wait()
#         event.clear()
#         print("New block")
#
#
# if __name__ == "__main__":
#     e_time_controller = Event()
#     e_time_scheduler = Event()
#     barrier_time_tick = Barrier(2)
#     barrier_new_block = Barrier(3)
#     controller_event = OrEventPair()
#     e_time_controller, e_new_block_controller = controller_event.get_events()[0], controller_event.get_events()[1]
#     scheduler_event = OrEventPair()
#     e_time_scheduler, e_new_block_scheduler = scheduler_event.get_events()[0], scheduler_event.get_events()[1]
#     scheduler = Thread(target=scheduler, args=(scheduler_event, [barrier_time_tick, barrier_new_block],), daemon=True)
#     controller = Thread(target=controller, args=(controller_event, [barrier_time_tick, barrier_new_block],), daemon=True)
#     ticker_controller = Thread(target=time_tick, args=(8, e_time_controller, barrier_time_tick,), daemon=True)
#     ticker_scheduler = Thread(target=time_tick, args=(9, e_time_scheduler, barrier_time_tick,), daemon=True)
#     block_reader = Thread(target=new_block,
#                           args=("c", [e_new_block_controller, e_new_block_scheduler], barrier_new_block,), daemon=True)
#     scheduler.start()
#     controller.start()
#     ticker_controller.start()
#     ticker_scheduler.start()
#     block_reader.start()
#     ticker_controller.join()
#     ticker_scheduler.join()
#     block_reader.join()
#     scheduler.join()
#     controller.join()

def time_tick(period, consumers):
    tick_number = 0
    while True:
        sleep(period)
        tick_number += 1
        for c in consumers:
            c.add_to_message_box("time_tick", str(tick_number))
        print("Time tick")


def new_block(consumers):
    while True:
        block_id = input("Enter new block ID:")
        for c in consumers:
            c.add_to_message_box("new_block", str(block_id))
        print("New block")


if __name__ == "__main__":
    controller = Consumer("controller", 10)
    scheduler = Consumer("scheduler", 9)
    threads = [
        Thread(target=time_tick, args=(20, [controller, scheduler],), daemon=True),
        Thread(target=new_block, args=([controller, scheduler],), daemon=True),
        Thread(target=controller.run, args=(), daemon=True),
        Thread(target=scheduler.run, args=(), daemon=True)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()
