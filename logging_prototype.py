from datetime import datetime
import os
import logging
from functools import wraps
from time import time, sleep

# initialize a basic logger
# by default this is the "root" logger
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(
  logging.Formatter("| %(asctime)s | %(name)s | %(levelname)s | %(message)s")
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def simple_logging_decorator(func):

  # function to be returned
  @wraps(func)
  def wrapper_func(*args, **kwargs):
    output = func()
    if output:
      logger.debug(output)
      # print("| {} | {} | {}".format(func.__name__, datetime.today().strftime("%Y-%m-%d %H:%M:%S"), output))
    else:
      logger.debug("")

  return wrapper_func


def timing_decorator(func):

  # function to be returned
  @wraps(func)
  def wrapper_func(*args, **kwargs):
    t0 = time()
    func(*args, **kwargs)
    t1 = time()
    logger.info("Execution time: %f s", t1-t0)

  return wrapper_func


@simple_logging_decorator
def print_directory():
  """Test docstring."""
  return os.getcwd()


@timing_decorator
def basic_sleep(duration):
  """Test docstring."""
  sleep(duration)


if __name__ == "__main__":
  print_directory()
  basic_sleep(1)
  # # add test for checking these!
  # print(print_directory.__name__)
  # print(print_directory.__doc__)
