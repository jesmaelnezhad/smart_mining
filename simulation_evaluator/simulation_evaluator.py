import os
import glob
from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS, is_new_simulation_going_to_happen
from data_bank import get_database_handler, get_simulation_database_handler
from nicehash import get_nice_hash_driver
from utility.log import logger


class SimulationEvaluator(TickPerformer):
    SIMULATION_PROOF_NAME_EXTENSION = '.simulation'

    def __init__(self):
        """
        A singleton class that is the simulation evaluator
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(
            EXECUTION_CONFIGS.simulation_evaluator_sleep_duration)
        self.simulation_db_handler = get_simulation_database_handler()
        self.simulation_driver = get_nice_hash_driver()

    def run(self, should_stop):
        # prepare the simulation database at the beginning of the evaluation
        proven_simulation_identifiers = None
        if EXECUTION_CONFIGS.clean_simulation_database:
            proven_simulation_identifiers = self.get_proven_simulation_identifiers()
        self.simulation_db_hander.prepare_for_simulation(
            proven_simulation_identifiers=proven_simulation_identifiers)
        # start taking samples if a new simulation is going to happen
        if not is_new_simulation_going_to_happen():
            return
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            logger('simulation/evaluator').debug("Updating evaluations at timestamp {0}.".format(current_timestamp))
            # fetch new order samples from the driver and record them in the database
            self.save_new_order_data_samples(current_timestamp=current_timestamp)
        # TODO: calculate the results of the evaluation and write it to file as proof

    def is_a_daemon(self):
        return False

    def save_new_order_data_samples(self, current_timestamp):
        all_orders = self.simulation_driver.get_orders()
        for o in all_orders:
            id = o.order_id
            limit = o.calculate_limit_at(current_timestamp)
            price = o.calculate_price_at(current_timestamp)
            self.simulation_db_handler.insert_order_info_sample(order_id=id,
                                                                timestamp=current_timestamp,
                                                                limit=limit,
                                                                price=price)

    def get_proven_simulation_identifiers(self):
        proven_identifiers = []

        directory_path = EXECUTION_CONFIGS.simulation_summaries_data_dir
        file_format = "*{0}".format(self.SIMULATION_PROOF_NAME_EXTENSION)
        file_search_pattern = os.path.join(directory_path, file_format)
        for file_name in glob.glob(file_search_pattern):
            if file_name not in self.data_files_loaded:
                simulation_identifier = os.path.basename(file_name)[
                                        :file_name.find(self.SIMULATION_PROOF_NAME_EXTENSION)]
                proven_identifiers.append(simulation_identifier)
        return proven_identifiers
