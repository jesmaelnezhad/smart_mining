from data_bank import mine_database as mine_db
from configuration import EXECUTION_CONFIGS
from utility.datetime_helpers import datetime_string_to_timestamp
from analyzer.analyzer import AverageWindowBlockCount
from utility.datetime_helpers import size_in_seconds

average_block_count = AverageWindowBlockCount(size_in_seconds(days=1),
                                              size_in_seconds(days=30))
average_block_count.set_latest_timestamp(datetime_string_to_timestamp('04/01/2020-0:0:0'))
# average_block_count.calculate_new_window_values_and_boundaries()
average_block_count.update_window_values()
values = average_block_count.get_window_values()
print(values)


# user = EXECUTION_CONFIGS.db_user
# password = EXECUTION_CONFIGS.db_password
# mine_db_handler = mine_db.MineDatabaseHandler(user, password)
# begin_timestamp = datetime_string_to_timestamp('04/05/2020-00:00:00')
# end_timestamp = datetime_string_to_timestamp('04/08/2020-00:00:00')
# blocks = mine_db_handler.get_blocks_between(begin_timestamp, end_timestamp)
# print(len(blocks))


# from datetime import datetime
#
# import pytz
#
# from utility.datetime_helpers import datetime_string_to_timestamp
#
# output_file = open('/home/jamshid/PycharmProjects/smart-miner/files/csv_data/blocks.05.01.2021-12.01.2021.mine.csv', 'w')
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