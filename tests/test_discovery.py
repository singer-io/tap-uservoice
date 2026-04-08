"""Test tap discovery mode and metadata."""
import unittest

from base import UservoiceBaseTest
from tap_tester.base_suite_tests.discovery_test import DiscoveryTest


class UservoiceDiscoveryTest(DiscoveryTest, UservoiceBaseTest):
    """Test tap discovery mode and metadata conforms to standards."""

    @staticmethod
    def name():
        return "tap_tester_uservoice_discovery_test"

    def streams_to_test(self):
        return self.expected_stream_names()
