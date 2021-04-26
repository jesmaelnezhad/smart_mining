from learner.learner import Learner

LEARNER = None


def get_learner():
    global LEARNER
    """
    :return: the learner object
    """
    if LEARNER is None:
        LEARNER = Learner()
    return LEARNER
