import unittest
from base import TapUservoiceBaseCase
from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest

class TapUservoiceAllFieldsTest(AllFieldsTest, TapUservoiceBaseCase):
    """Standard All Fields Test"""

    @staticmethod
    def name():
        return 'uservoice_all_fields'

    def streams_to_test(self):
        return self.expected_stream_names() - {
            'requests',
            'teams',
            'comments',
            'nps_ratings',
            'supporters',
            'labels',
            'segments',
            'segmented_values',
            'product_areas',
            'feature_statuses'
        }
