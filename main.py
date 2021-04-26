import sys
import traceback
from time import sleep

from clock import get_clock
from configuration import EXECUTION_CONFIGS, is_simulation
from learner import get_learner
from nicehash import get_nice_hash_driver
from simulation_evaluator import get_simulation_evaluator
from utility import log
from analyzer import get_analyzer
from controller import get_controller
from data_bank import get_database_handler, get_database_updater, get_simulation_database_updater


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

        # start the mine database updater
        mine_database_updater = get_database_updater()
        mine_database_updater.start()
        TICK_PERFORMERS.append(mine_database_updater)
        log.logger('main').info('Mine database updater started.')

        if is_simulation():
            # start the simulation database updater
            simulation_database_updater = get_simulation_database_updater()
            simulation_database_updater.start()
            TICK_PERFORMERS.append(simulation_database_updater)
            log.logger('main').info('Simulation database updater started.')

        # start the controller
        CONTROLLER = get_controller()
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

        # start the nice hash driver
        nice_hash = get_nice_hash_driver()
        nice_hash.start()
        TICK_PERFORMERS.append(nice_hash)
        log.logger('main').info('Nice hash driver started.')

        if is_simulation():
            # start the simulation evaluator
            simulation_evaluator = get_simulation_evaluator()
            simulation_evaluator.start()
            TICK_PERFORMERS.append(simulation_evaluator)
            log.logger('main').info('Simulation evaluator started.')
            while not simulation_evaluator.should_end_execution():
                sleep(1)
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
