"""Test that with no fields selected for a stream automatic fields are still
replicated."""
from base import UservoiceBaseTest
from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest


class UservoiceAutomaticFields(MinimumSelectionTest, UservoiceBaseTest):
    """Test that with no fields selected for a stream automatic fields are
    still replicated."""

    @staticmethod
    def name():
        return "tap_tester_uservoice_automatic_fields_test"

    def streams_to_test(self):
        return self.expected_stream_names()
