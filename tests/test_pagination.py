from tap_tester.base_suite_tests.pagination_test import PaginationTest
from base import UservoiceBaseTest


class UservoicePaginationTest(PaginationTest, UservoiceBaseTest):
    """
    Ensure tap can replicate multiple pages of data for streams that use pagination.
    """

    @staticmethod
    def name():
        return "tap_tester_uservoice_pagination_test"

    def streams_to_test(self):
        return self.expected_stream_names()
