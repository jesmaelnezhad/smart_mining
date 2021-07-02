import enum
from threading import Lock
from time import sleep

from string_utils import random_string

from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from configuration.constants import VIRTUAL_ORDER_ID_STRING_SIZE
from utility.log import logger
from clock import get_clock
from utility.containers import PersistentThreadSafeDictionary, PersistentObject


class VirtualOrderStatus(enum.Enum):
    NOT_SET = "NOT_SET"
    OK = "OK"
    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"


class VirtualOrder(PersistentObject):
    """
    The class that represents a virtual order.
    """

    def __init__(self, owner, virtual_order_id, order_id,
                 power_limit_request,
                 request_creation_timestamp,
                 request_expiration_timestamp):
        super(VirtualOrder, self).__init__(owner, virtual_order_id)
        self.virtual_order_id = virtual_order_id
        self.order_id = order_id
        self.power_limit_request = float(power_limit_request)
        self.request_creation_timestamp = int(request_creation_timestamp)
        self.request_expiration_timestamp = int(request_expiration_timestamp)
        self.status = VirtualOrderStatus.NOT_SET

    def recast_attr_types_after_load(self):
        self.power_limit_request = float(self.power_limit_request)
        self.request_creation_timestamp = int(self.request_creation_timestamp)
        self.request_expiration_timestamp = int(self.request_expiration_timestamp)
        self.status = VirtualOrderStatus(self.status)

    def get_virtual_order_id(self):
        return self.virtual_order_id

    def get_order_id(self):
        return self.order_id

    def get_power_limit_request(self):
        return self.power_limit_request

    def get_creation_timestamp(self):
        return self.request_creation_timestamp

    def get_expiration_timestamp(self):
        return self.request_expiration_timestamp

    def is_valid_at(self, up_to_timestamp=None):
        if up_to_timestamp is None:
            up_to_timestamp = get_clock().read_timestamp_of_now()
        return self.get_expiration_timestamp() < up_to_timestamp

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status


class VirtualOrdersHandler:
    VIRTUAL_ORDERS_OWNER_NAME = "VIRTUAL_ORDERS_HANDLER"

    def __init__(self, orders_db_handler):
        self.orders_db = orders_db_handler
        self.virtual_orders = PersistentThreadSafeDictionary(self.orders_db)
        self.virtual_order_ids_mutex = Lock()

    def load_state_from_database_or_init(self):
        self.virtual_order_ids_mutex.acquire()
        try:
            all_virtual_order_keys = self.orders_db.key_value_get_owner_all_keys(self.VIRTUAL_ORDERS_OWNER_NAME)
            for virtual_order_key in all_virtual_order_keys:
                obj = VirtualOrder(self.VIRTUAL_ORDERS_OWNER_NAME, virtual_order_key,
                                   order_id='',
                                   power_limit_request=0,
                                   request_creation_timestamp=0,
                                   request_expiration_timestamp=0)
                self.virtual_orders.set(virtual_order_key, obj)
            self.virtual_orders.load_objects()
        finally:
            self.virtual_order_ids_mutex.release()

    def save_state_in_database(self):
        self.virtual_orders.save_objects()

    def remove_expired_orders(self, up_to_timestamp=None):
        self.virtual_order_ids_mutex.acquire()
        try:
            self.virtual_orders.clear_by_predicate(VirtualOrder.is_valid_at, {'up_to_timestamp': up_to_timestamp})
        finally:
            self.virtual_order_ids_mutex.release()

    def get_new_virtual_order_id(self):
        self.virtual_order_ids_mutex.acquire()
        try:
            all_virtual_order_keys = self.orders_db.key_value_get_owner_all_keys(self.VIRTUAL_ORDERS_OWNER_NAME)
            new_key = random_string(VIRTUAL_ORDER_ID_STRING_SIZE)
            while new_key not in all_virtual_order_keys:
                new_key = random_string(VIRTUAL_ORDER_ID_STRING_SIZE)
            self.virtual_orders.set(new_key, VirtualOrder(self.VIRTUAL_ORDERS_OWNER_NAME, new_key,
                                                          order_id='',
                                                          power_limit_request=0,
                                                          request_creation_timestamp=0,
                                                          request_expiration_timestamp=0))
            return new_key
        finally:
            self.virtual_order_ids_mutex.release()

    def set_virtual_order(self, virtual_order_id,
                          order_id,
                          power_limit_request,
                          creation_timestamp,
                          expiration_timestamp):
        virtual_order_obj = VirtualOrder(owner=self.VIRTUAL_ORDERS_OWNER_NAME,
                                         virtual_order_id=virtual_order_id,
                                         order_id=order_id,
                                         power_limit_request=power_limit_request,
                                         request_creation_timestamp=creation_timestamp,
                                         request_expiration_timestamp=expiration_timestamp)
        self.virtual_orders.set(virtual_order_id, virtual_order_obj)

    def set_virtual_order_status(self, virtual_order_id, status):
        self.virtual_orders.call_method_from_object(VirtualOrder.set_status, {'status': status}, virtual_order_id)

    def delete_virtual_order(self, virtual_order_id):
        self.virtual_order_ids_mutex.acquire()
        try:
            return self.virtual_orders.unset(virtual_order_id)
        finally:
            self.virtual_order_ids_mutex.release()

    def get_virtual_order(self, virtual_order_id):
        """

        :param virtual_order_id:
        :return: Tuple (power limit request, creation ts, expiration ts) or None if not exists
        """
        virtual_order_obj = self.virtual_orders.get(virtual_order_id)
        if virtual_order_obj is None:
            return None
        return (virtual_order_obj.get_power_limit_request(),
                virtual_order_obj.get_creation_timestamp(),
                virtual_order_obj.get_expiration_timestamp(),)

    def get_aggregated_virtual_order_limits(self, up_to_timestamp=None):
        """
        Returns the sums grouped by order_id
        :return: a dictionary from order_id to tuple of (list of power limits, list of virtual order ids)
        """
        data = self.virtual_orders.snapshot()
        order_buckets_limits = dict()
        order_buckets_virtual_order_ids = dict()
        for container_virtual_order_key, virtual_order in data.items():
            is_valid = virtual_order.is_valid_at(up_to_timestamp=up_to_timestamp)
            if not is_valid:
                continue
            power_limit_request = virtual_order.get_power_limit_request()
            virtual_order_id = virtual_order.get_virtual_order_id()
            order_id = virtual_order.get_order_id()
            if order_id not in order_buckets_limits.keys():
                order_buckets_limits[order_id] = list()
                order_buckets_virtual_order_ids[order_id] = list()
            order_buckets_limits[order_id].append(power_limit_request)
            order_buckets_virtual_order_ids[order_id].append(virtual_order_id)
        return {order_id: (order_buckets_limits[order_id], order_buckets_virtual_order_ids[order_id]) for order_id in
                order_buckets_limits.keys()}


class VirtualOrdersUpdater(TickPerformer):
    def __init__(self, orders_db_handler):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(
            EXECUTION_CONFIGS.virtual_order_updater_sleep_duration)
        self.virtual_orders = VirtualOrdersHandler(orders_db_handler=orders_db_handler)

    def get_virtual_orders_handler(self):
        return self.virtual_orders

    def run(self, should_stop):
        self.virtual_orders.load_state_from_database_or_init()
        while True:
            if should_stop():
                break
            messages = dict()
            try:
                self.message_box_changed.acquire()
                self.message_box_changed.wait(self.tick_duration)
                messages = self.message_box.snapshot(should_clear=True)
            finally:
                self.message_box_changed.release()
            # messages can be used from here.
            current_timestamp = get_clock().read_timestamp_of_now()
            # remove expired orders
            self.virtual_orders.remove_expired_orders(up_to_timestamp=current_timestamp)
            # save virtual orders in database
            self.virtual_orders.save_state_in_database()

    def post_run(self):
        logger('virtual order/updater').info("Updater is terminating.")

    def is_a_daemon(self):
        return True
