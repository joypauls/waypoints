import logging
import structlog
import time

"""
Implementing a DAG/Tree of processors:

In general: not sure
Simple diverging paths? could just make a class with only side effects as a secondary branch
"""


class PrettyTimestamp:
  """
  Handles some formatting for dev use cases
  """
  def __init__(self, input_format: str, keep_original: bool = False):
    self.input_format = input_format
    self.keep_original = keep_original

  def __call__(self, logger, method_name, event_dict):
    """
    Makes this callable! Processors take the above ^ args

    >>> cd = ConditionalDropper("127.0.0.1")
    >>> cd(None, None, {"event": "foo", "peer": "10.0.0.1"})
    {'peer': '10.0.0.1', 'event': 'foo'}
    """
    if event_dict.get("timestamp"):
      # handle flag to keep original timestamp
      if self.keep_original:
        event_dict["raw_timestamp"] = event_dict["timestamp"]
      # handle different formats
      if self.input_format == "unix":
        event_dict["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event_dict["timestamp"]))
      return event_dict
    else:
      return event_dict


structlog.configure(
    processors=[
        # defaults?
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        # adds in a timestamp key/val
        structlog.processors.TimeStamper(),
        # post-processing? is this a bad idea?
        PrettyTimestamp(input_format="unix"),
        # pick a renderer for the last processor in the chain!
        structlog.dev.ConsoleRenderer(),
        # structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
)
logger = structlog.get_logger()


def test(input: dict):
  log = logger.bind(
    id="12345678",
  )
  if input.get("letter"):
    log = log.bind(letter=input["letter"])

  log.msg(input.get("message"))


if __name__ == "__main__":
  test({"letter": "A", "message": "blah"})
  test({"message": "fdjfhsajdfg"})
  test({"message": "hey world"})
