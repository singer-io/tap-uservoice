from base import UservoiceBaseTest
from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest


class UservoiceAllFields(AllFieldsTest, UservoiceBaseTest):
    """Ensure running the tap with all streams and fields selected results in
    the replication of all fields."""

    @staticmethod
    def name():
        return "tap_tester_uservoice_all_fields_test"

    def streams_to_test(self):
        return self.expected_stream_names()
