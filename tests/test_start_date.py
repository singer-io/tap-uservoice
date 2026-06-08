from base import UservoiceBaseTest
from tap_tester.base_suite_tests.start_date_test import StartDateTest


class UservoiceStartDateTest(StartDateTest, UservoiceBaseTest):
    """Instantiate start date according to the desired data set and run the
    test."""

    @staticmethod
    def name():
        return "tap_tester_uservoice_start_date_test"

    def streams_to_test(self):
        return self.expected_stream_names()

    @property
    def start_date_1(self):
        return "2015-01-01T00:00:00Z"

    @property
    def start_date_2(self):
        return "2025-09-01T00:00:00Z"
