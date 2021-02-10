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