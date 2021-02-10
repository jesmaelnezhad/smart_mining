from simulation_evaluator.simulation_evaluator import SimulationEvaluator

SIMULATION_EVALUATOR = None


def get_simulation_evaluator():
    global SIMULATION_EVALUATOR
    """
    :return: the controller object
    """
    if SIMULATION_EVALUATOR is None:
        SIMULATION_EVALUATOR = SimulationEvaluator()
    return SIMULATION_EVALUATOR
