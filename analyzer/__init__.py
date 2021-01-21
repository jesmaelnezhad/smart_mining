from analyzer.analyzer import Analyzer

ANALYZER = None


def get_analyzer():
    global ANALYZER
    """
    :return: the analyzer object
    """
    if ANALYZER is None:
        ANALYZER = Analyzer()
    return ANALYZER
