import functools
import logging
import time

import newrelic.agent

logger = logging.getLogger(__name__)


def newrelic_timing_metric(metric_name):
    def inner(func):
        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            start_time = time.perf_counter()
            value = func(*args, **kwargs)
            end_time = time.perf_counter()
            run_time = end_time - start_time
            logger.info(f"{metric_name} executed in {run_time:.4f} secs")
            newrelic.agent.record_custom_metric(f"Custom/{metric_name}", run_time)
            return value

        return wrapper_timer

    return inner
