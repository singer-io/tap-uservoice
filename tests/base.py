import os
import unittest

from tap_tester import connections, menagerie, runner
from tap_tester.logger import LOGGER
from tap_tester.base_suite_tests.base_case import BaseCase


class UservoiceBaseTest(BaseCase):
    """Setup expectations for test sub classes.

    Metadata describing streams. A bunch of shared methods that are used
    in tap-tester tests. Shared tap-specific methods (as needed).
    """
    start_date = "2019-01-01T00:00:00Z"

    @staticmethod
    def tap_name():
        """The name of the tap."""
        return "tap-uservoice"

    @staticmethod
    def get_type():
        """The expected url route ending."""
        return "platform.uservoice"

    @classmethod
    def expected_metadata(cls):
        """The expected streams and metadata about the streams.

        All Uservoice streams use INCREMENTAL replication with
        updated_at as the replication key and id as primary key.
        """
        return {
            "categories": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "comments": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "external_accounts": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "external_users": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "feature_statuses": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "features": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "forums": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "labels": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "nps_ratings": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "product_areas": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "requests": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "segmented_values": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "segments": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "status_updates": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "statuses": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "suggestions": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "supporters": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "teams": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
            "users": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updated_at"},
                cls.RESPECTS_START_DATE: True,
                cls.API_LIMIT: 100,
            },
        }

    @staticmethod
    def get_credentials():
        """Authentication information for the test account."""
        return {
            'api_key': os.getenv('TAP_USERVOICE_API_KEY'),
            'api_secret': os.getenv('TAP_USERVOICE_API_SECRET'),
        }

    def get_properties(self, original: bool = True):
        """Configuration of properties required for the tap."""
        return {
            'subdomain': os.getenv('TAP_USERVOICE_SUBDOMAIN'),
            'api_key': os.getenv('TAP_USERVOICE_API_KEY'),
            'api_secret': os.getenv('TAP_USERVOICE_API_SECRET'),
            'start_date': self.start_date,
        }
