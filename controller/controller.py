import json
from time import sleep

import requests

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS, is_simulation
from controller.scheduler.ssr import SSRLoader
from data_bank.blocks import get_database_handler
from utility.log import logger


## TODO change controller to work with virtual order handler object to use virtual orders for SSRs
"""
At start:
  Check database and load the state of active strategies from the database into memory
  and create and bootstrap the StrategyStateMachine object for each one.

At each reconcile:
  1. Check all SSRs in the 'files/strategies' directory and create and bootstrap a
  StrategyStateMachine object for each one that doesn'controller have one in the database. 
"""


class Controller(TickPerformer):
    TEMPORARY_ORDER_ID = "13131-43524dsfse-f23edfw4rfs-rfer-w4rt5ystet-w34tw3r3"

    def __init__(self, scope_identifier):
        """
        A singleton class that is the controller
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.controller_sleep_duration)
        self.scope_identifier = scope_identifier
        current_timestamp = get_clock().read_timestamp_of_now()
        self.active_order = None
        self.init_active_order_info(current_timestamp)
        self.latest_block_id = None
        self.latest_block_moment = None


        self.block_has_just_solved = False


        self.update_latest_block_id(current_timestamp)



        self.cdf50_is_step_on = False

    def get_nice_hash_driver(self):
        return self.scope_identifier.get_nice_hash_driver()

    def init_active_order_info(self, current_timestamp):
        """
        Creates the ActiveOrderInfo object either from the real order that's returned from nicehash API, or from scratch
        in the case of simulation.
        :return: An ActiveOrderInfo object that represents the order being used by the controller
        """
        orders = self.get_nice_hash_driver().get_orders(order_id=None)
        if len(orders) > 1:
            logger("controller/init_order").warn("Having more than one order!!!")
            logger("controller/init_order").warn("Orders: {0}", "\n".join(orders))
            self.active_order = orders[0]
        elif len(orders) == 1:
            self.active_order = orders[0]
        else:
            # no orders, so we are going to create one
            # FIXME the initial price and limit may need to be refined
            # FIXME the initial budget_left value also may need to be given
            limit = EXECUTION_CONFIGS.controller_cdf50_power_off_limit
            price = EXECUTION_CONFIGS.controller_cdf50_power_off_price
            self.active_order = self.get_nice_hash_driver().create_order(
                creation_timestamp=current_timestamp, order_id=self.TEMPORARY_ORDER_ID,
                price=price, speed_limit=limit, amount=None,
                exists=True)

    def order_turn_on_off(self, turn_on, current_timestamp):
        """
        Turns on or off the active order of the controller based on the given flag
        :return: None
        """
        # FIXME: may need to be refined
        limit_step = EXECUTION_CONFIGS.controller_cdf50_power_limit_step
        price_step = EXECUTION_CONFIGS.controller_cdf50_power_price_step
        if turn_on:
            self.get_nice_hash_driver().update_order_price_and_limit(timestamp=current_timestamp,
                                                                     order_id=self.active_order.order_id,
                                                                     limit_change=limit_step, price_change=price_step)
            self.cdf50_is_step_on = True
        else:
            self.get_nice_hash_driver().update_order_price_and_limit(timestamp=current_timestamp,
                                                                     order_id=self.active_order.order_id,
                                                                     limit_change=-1 * limit_step,
                                                                     price_change=-1 * price_step)
            self.cdf50_is_step_on = False

    def update_latest_block_id(self, current_timestamp):
        """
        Updates the id of the latest block in the mine database (prior to the current_timestamp)
        :return: None
        """
        db_handler = get_database_handler()
        id, moment = db_handler.get_latest_block_info(prior_to_moment=current_timestamp)
        if self.latest_block_id is None:
            self.latest_block_id = id
            self.latest_block_moment = moment
            # self.block_has_just_solved = True
        else:
            if id == self.latest_block_id:
                self.block_has_just_solved = False
            else:
                self.latest_block_id = id
                self.latest_block_moment = moment
                self.block_has_just_solved = True

    def run(self, should_stop):

        loader = SSRLoader()

        ssr = loader.load_ssr_by_name("strategy1")
        logger("ssr").info(json.dumps(ssr.get_dict()))

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
            # Unless it is a simulation, declare liveness to the healthcheck API
            if not is_simulation():
                # poke healthcheck API
                self.poke_health_check()
            # Do controller work
            current_timestamp = get_clock().read_timestamp_of_now()
            # Update the state of the controller
            # 1. update the latest block id and set the just_solved flag
            self.update_latest_block_id(current_timestamp=current_timestamp)

            # Make actions if needed
            # # CDF50 strategy
            # if self.cdf50_is_step_on:
            #     # if on, turn off if too much time has passed (more than cdf 50)
            #     if current_timestamp - self.latest_block_moment > EXECUTION_CONFIGS.controller_cdf50_order_lifespan_duration:
            #         self.order_turn_on_off(turn_on=False, current_timestamp=current_timestamp)
            # else:
            #     # if off, turn on if a new block has arrived
            #     if self.block_has_just_solved:
            #         self.order_turn_on_off(turn_on=True, current_timestamp=current_timestamp)
            #
            # calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.controller_cdf50_order_lifespan_duration)
            logger('controller').debug("Updating controller at timestamp {0}.".format(current_timestamp))
            pass
        # Do house-keeping before termination
        self.pre_termination_house_keeping()
        # Let the main logic know it does not have to wait for the controller and
        # turn off other threads

    def pre_termination_house_keeping(self):
        logger('controller').debug("Doing house keeping before termination")
        # TODO
        pass

    def post_run(self):
        logger('controller').info("Controller is terminating.")

    def is_a_daemon(self):
        return False

    def poke_health_check(self):
        health_check_url = "http://{0}:{1}".format(EXECUTION_CONFIGS.healthcheck_listen_address,
                                                   EXECUTION_CONFIGS.healthcheck_listen_port)
        try:
            r = requests.get(health_check_url)
            if r.status_code == '200':
                logger("controller").warn(
                    "Could not poke health check. This can result in all orders being closed because of health check panic.")
            else:
                logger("controller").debug("Poked health check successfully.")
        except Exception as e:
            logger("controller").warn(
                "Could not poke health check. This can result in all orders being closed because of health check panic.")
            logger("controller").error("Healthcheck poking error: {0}".format(e))
