import unittest
from base import TapUservoiceBaseCase
from tap_tester.base_suite_tests.discovery_test import DiscoveryTest

class TapUservoiceDiscoveryTest(DiscoveryTest, TapUservoiceBaseCase):
    """Standard Discovery Test"""

    @staticmethod
    def name():
        return 'uservoice_discovery'

    def streams_to_test(self):
        return self.expected_stream_names()

    # @unittest.expectedFailure
    # def test_replication_metadata(self):
    #     """This test will fail until forced-replication-key is added to stream metadata"""
    #     super().test_replication_metadata()
