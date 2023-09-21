from locust import constant_pacing

from functions.performance_test import PerformanceTest


class LoadTest(PerformanceTest):
    """This class is to run the load test.

    This is a slower version of the stress test by using constant_pacing.
    """

    wait_time = constant_pacing(10)
