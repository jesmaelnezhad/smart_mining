import sys
import traceback
from time import sleep

from clock import get_clock
from configuration import EXECUTION_CONFIGS, is_simulation, is_healthcheck
from data_bank import get_database_updater, get_simulation_database_updater
from data_bank.orders import get_orders_database_updater, get_virtual_orders_updater, get_simulation_scope_identifier
from healthcheck import get_health_check_watcher
from healthcheck.server import start_healthcheck_server
from learner import get_learner
from data_bank.orders.vitual_order_request_applier import get_request_applier
from simulation_evaluator import get_simulation_evaluator
from utility import log
from analyzer import get_analyzer
from controller import get_controller

TICK_PERFORMERS = []
CONTROLLER = None


def join_tick_performers(stop=False):
    if stop:
        for p in TICK_PERFORMERS:
            p.stop()
    for p in TICK_PERFORMERS:
        p.join()


def graceful_termination():
    if CONTROLLER is None:
        # stop all threads since controller is not running anyways
        join_tick_performers(stop=True)
    else:
        # first stop the controller and wait for it to terminate gracefully
        CONTROLLER.stop()
        while not CONTROLLER.should_end_execution():
            sleep(1)
        join_tick_performers(stop=True)


if __name__ == '__main__':
    try:
        log.logger('main').info('Execution identifier is {0}'.format(EXECUTION_CONFIGS.execution_identifier))
        # start the clock
        clock = get_clock()
        clock.start()
        TICK_PERFORMERS.append(clock)
        log.logger('main').info('Clock started.')

        # # start the nice hash driver
        # nice_hash = get_nice_hash_driver()
        # nice_hash.start()
        # TICK_PERFORMERS.append(nice_hash)
        # log.logger('main').info('Nice hash driver started.')

        if is_healthcheck():
            # start healthcheck watcher
            health_check_watcher = get_health_check_watcher()
            health_check_watcher.start()
            TICK_PERFORMERS.append(health_check_watcher)
            log.logger('main').info('Health check watcher started.')
        else:
            # start the mine database updater
            mine_database_updater = get_database_updater()
            mine_database_updater.start()
            TICK_PERFORMERS.append(mine_database_updater)
            log.logger('main').info('Mine database updater started.')

            scope_simulation_identifier = get_simulation_scope_identifier()

            # start the orders database updater
            orders_database_updater = get_orders_database_updater(scope_simulation_identifier)
            orders_database_updater.start()
            TICK_PERFORMERS.append(orders_database_updater)
            log.logger('main').info('Orders database updater started.')

            # start the virtual orders updater
            virtual_orders_updater = get_virtual_orders_updater(scope_simulation_identifier)
            virtual_orders_updater.start()
            TICK_PERFORMERS.append(virtual_orders_updater)
            log.logger('main').info('Virtual orders updater started.')

            # start the virtual order request applier
            request_applier = get_request_applier(scope_identifier=scope_simulation_identifier)
            request_applier.start()
            TICK_PERFORMERS.append(request_applier)
            log.logger('main').info('Virtual orders request applier started.')

            if is_simulation():
                # start the simulation database updater
                simulation_database_updater = get_simulation_database_updater()
                simulation_database_updater.start()
                TICK_PERFORMERS.append(simulation_database_updater)
                log.logger('main').info('Simulation database updater started.')

            # start the controller
            CONTROLLER = get_controller(scope_identifier=scope_simulation_identifier)
            CONTROLLER.start()
            TICK_PERFORMERS.append(CONTROLLER)
            log.logger('main').info('Controller started.')

            # start the analyzer
            analyzer = get_analyzer()
            analyzer.start()
            TICK_PERFORMERS.append(analyzer)
            log.logger('main').info('Analyzer started.')

            # start the learner
            learner = get_learner()
            learner.start()
            TICK_PERFORMERS.append(learner)
            log.logger('main').info('Learner started.')

        if is_simulation():
            # start the simulation evaluator
            simulation_evaluator = get_simulation_evaluator()
            simulation_evaluator.start()
            TICK_PERFORMERS.append(simulation_evaluator)
            log.logger('main').info('Simulation evaluator started.')
            while not simulation_evaluator.should_end_execution():
                sleep(1)
            graceful_termination()
        elif is_healthcheck():
            # start the liveness decalation API
            start_healthcheck_server()
            graceful_termination()
        else:
            join_tick_performers()
    except KeyboardInterrupt:
        log.logger('main').info('Program terminating upon keyboard interrupt.')
        graceful_termination()
    except Exception as e:
        log.logger('main').info("Exception {0}".format(e))
        traceback.print_exc(file=sys.stdout)
        graceful_termination()
        sys.exit(1)
    sys.exit(0)
