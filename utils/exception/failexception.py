from utils import *

class FailException(BaseException):
    """The parent of all test exceptions."""
    # Children are required to override this.  Never instantiate directly.
    def __init__(self, error_message):
        logger.error(error_message)
