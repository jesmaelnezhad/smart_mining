from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from data_bank.orders import get_virtual_orders_handler, get_orders_database_handler
from data_bank.orders.virtual_orders_handler import VirtualOrderRequest
from utility.log import logger


class VirtualOrderRequestApplier(TickPerformer):
    def __init__(self, scope_identifier):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(
            EXECUTION_CONFIGS.virtual_order_applier_sleep_duration)
        self.virtual_order_handler = get_virtual_orders_handler(scope_identifier)
        self.orders_database_handler = get_orders_database_handler(scope_identifier)
        self.scope_identifier = scope_identifier

    def get_nice_hash_driver(self):
        self.scope_identifier.get_nice_hash_driver()

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            report = self.virtual_order_handler.get_overall_requests(up_to_timestamp=current_timestamp)
            for order_id, request_summary in report.items():
                orders_sum_list = request_summary[0]
                orders_virtual_order_ids_list = request_summary[1]
                order_list = self.orders_database_handler.get_orders(order_id=order_id)
                if len(order_list) == 0:
                    for virtual_order_id in orders_virtual_order_ids_list:
                        self.virtual_order_handler.set_virtual_order_request_status(virtual_order_id=virtual_order_id,
                                                                                    order_id=order_id,
                                                                                    status=VirtualOrderRequest.Status.ORDER_NOT_FOUND)
                else:
                    order = order_list[0]
                    order_price = order[0]
                    order_limit = order[1]
                    order_amount = order[2]
                    limit_request = sum(orders_sum_list)
                    limit_change = limit_request - order_limit
                    self.nice_hash_driver.update_order_price_and_limit(timestamp=current_timestamp,
                                                                       order_id=order_id,
                                                                       limit_change=limit_change)

    def post_run(self):
        logger('virtual order/applier').info("Applier is terminating.")

    def is_a_daemon(self):
        return True
