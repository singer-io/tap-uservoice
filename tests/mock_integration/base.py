"""
Base test class for mock integration tests for tap-uservoice.

These tests run the real tap code against mocked API responses -- no external
tap-tester dependency required.

**Architecture**
* ``MockDataGenerator`` (in mock_data_generator.py) -- generic, reusable
  mock data generator.  Reads inline schemas and produces deterministic,
  type-conformant mock records.
* ``STREAM_CONFIG`` -- tap-specific configuration that describes response
  formats.
* ``UservoiceMockBaseTest`` -- tap-specific test base that wires the
  generator to the tap's real sync logic.
"""
import copy
from datetime import timedelta, timezone
from unittest.mock import MagicMock

from singer import metadata

import tap_uservoice
from tap_uservoice.streams import AVAILABLE_STREAMS
from .mock_data_generator import MockDataGenerator


# ------------------------------------------------------------------ #
#  Stream configuration
# ------------------------------------------------------------------ #

# Build stream config from AVAILABLE_STREAMS
STREAM_CONFIG = {}
for _stream_cls in AVAILABLE_STREAMS:
    STREAM_CONFIG[_stream_cls.TABLE] = {
        'stream_cls': _stream_cls,
        'record_count': 2,
    }

# Map TABLE name -> stream class
STREAM_CLASS_MAP = {s.TABLE: s for s in AVAILABLE_STREAMS}

# Seed for "second sync" records
RECENT_DATA_SEED = 100


# ------------------------------------------------------------------ #
#  Test base class
# ------------------------------------------------------------------ #

class UservoiceMockBaseTest:
    """Shared helpers and dynamically-generated mock data for
    uservoice mock integration tests."""

    PRIMARY_KEYS = "primary_keys"
    REPLICATION_METHOD = "replication_method"
    REPLICATION_KEYS = "replication_keys"

    STREAM_CONFIG = STREAM_CONFIG

    default_config = {
        "subdomain": "mock-subdomain",
        "api_key": "mock-api-key",
        "api_secret": "mock-api-secret",
        "start_date": "2024-06-14T00:00:00Z",
    }

    ALL_STREAM_IDS = set(STREAM_CONFIG.keys())

    # ------------------------------------------------------------------ #
    #  Convenience helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def get_expected_record_count(cls, stream_name):
        """Number of records the default mock client returns for a stream."""
        return STREAM_CONFIG[stream_name]['record_count']

    @classmethod
    def get_mock_records(cls, stream_name, count=None, base_seed=0):
        """Return the mock records that the API would return for a stream."""
        stream_cls = STREAM_CLASS_MAP[stream_name]
        n = count if count is not None else STREAM_CONFIG[stream_name]['record_count']
        return MockDataGenerator.generate_records(stream_cls, n, base_seed=base_seed)

    @classmethod
    def get_initial_bookmark_date(cls):
        """A date guaranteed to be *before* any generated mock date."""
        dt = MockDataGenerator.BASE_DATE - timedelta(days=1)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    @classmethod
    def get_recent_record(cls, stream_name):
        """Return the 'recent' mock record used in date-filter tests."""
        return cls.get_mock_records(stream_name, count=1, base_seed=RECENT_DATA_SEED)[0]

    @classmethod
    def get_recent_date(cls, stream_name):
        """Return the updated_at value from the 'recent' mock record."""
        return cls.get_recent_record(stream_name).get('updated_at', '')

    # ------------------------------------------------------------------ #
    #  Expected metadata
    # ------------------------------------------------------------------ #

    @classmethod
    def expected_metadata(cls):
        result = {}
        for stream_cls in AVAILABLE_STREAMS:
            result[stream_cls.TABLE] = {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: "INCREMENTAL",
                cls.REPLICATION_KEYS: {"updated_at"},
            }
        return result

    # ------------------------------------------------------------------ #
    #  Mock client factories
    # ------------------------------------------------------------------ #

    @classmethod
    def _create_mock_client(cls, record_count=None):
        """Create a mock UservoiceClient that returns generated data."""
        client = MagicMock()
        client.config = dict(cls.default_config)
        client.access_token = 'mock_token'

        def mock_fetch_data(url, updated_after=None, updated_before=None,
                            cursor=None, endpoint=None, tries=0):
            stream_name = endpoint
            if stream_name and stream_name in STREAM_CLASS_MAP:
                stream_cls = STREAM_CLASS_MAP[stream_name]
                n = record_count if record_count is not None else \
                    STREAM_CONFIG[stream_name]['record_count']
                records = MockDataGenerator.generate_records(stream_cls, n)
                return {
                    stream_name: copy.deepcopy(records),
                    'pagination': {
                        'cursor': None,
                        'total_pages': 1,
                    }
                }
            return {'pagination': {'cursor': None, 'total_pages': 0}}

        client.fetch_data = MagicMock(side_effect=mock_fetch_data)
        return client

    @classmethod
    def _create_paginated_mock_client(cls):
        """Mock client that returns 2-page results."""
        client = MagicMock()
        client.config = dict(cls.default_config)
        client.access_token = 'mock_token'

        call_counts = {}

        def mock_fetch_data(url, updated_after=None, updated_before=None,
                            cursor=None, endpoint=None, tries=0):
            stream_name = endpoint
            if stream_name and stream_name in STREAM_CLASS_MAP:
                stream_cls = STREAM_CLASS_MAP[stream_name]
                key = f"{stream_name}:{updated_after}"
                call_counts.setdefault(key, 0)
                call_counts[key] += 1

                if call_counts[key] == 1:
                    # First page
                    records = MockDataGenerator.generate_records(
                        stream_cls, 1, base_seed=0)
                    return {
                        stream_name: copy.deepcopy(records),
                        'pagination': {
                            'cursor': 'page2_cursor',
                            'total_pages': 2,
                        }
                    }
                else:
                    # Second page
                    records = MockDataGenerator.generate_records(
                        stream_cls, 1, base_seed=10)
                    return {
                        stream_name: copy.deepcopy(records),
                        'pagination': {
                            'cursor': None,
                            'total_pages': 2,
                        }
                    }
            return {'pagination': {'cursor': None, 'total_pages': 0}}

        client.fetch_data = MagicMock(side_effect=mock_fetch_data)
        return client

    @classmethod
    def _create_date_filtering_mock_client(cls):
        """Mock client that returns different results when updated_after
        is more recent (simulating bookmark-based filtering)."""
        client = MagicMock()
        client.config = dict(cls.default_config)
        client.access_token = 'mock_token'

        def mock_fetch_data(url, updated_after=None, updated_before=None,
                            cursor=None, endpoint=None, tries=0):
            stream_name = endpoint
            if stream_name and stream_name in STREAM_CLASS_MAP:
                stream_cls = STREAM_CLASS_MAP[stream_name]
                # If updated_after is recent, return "recent" data
                base_date_aware = MockDataGenerator.BASE_DATE.replace(
                    tzinfo=timezone.utc)
                if updated_after and updated_after > base_date_aware:
                    records = MockDataGenerator.generate_records(
                        stream_cls, 1, base_seed=RECENT_DATA_SEED)
                else:
                    records = MockDataGenerator.generate_records(
                        stream_cls,
                        STREAM_CONFIG[stream_name]['record_count'])
                return {
                    stream_name: copy.deepcopy(records),
                    'pagination': {
                        'cursor': None,
                        'total_pages': 1,
                    }
                }
            return {'pagination': {'cursor': None, 'total_pages': 0}}

        client.fetch_data = MagicMock(side_effect=mock_fetch_data)
        return client

    # ------------------------------------------------------------------ #
    #  Discover / catalog helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_discover(cls):
        """Run discovery using real stream classes and return catalog
        entry dicts."""
        config = dict(cls.default_config)
        state = {}
        catalog_entries = []
        for available_stream in AVAILABLE_STREAMS:
            stream = available_stream(config, state, None, None)
            catalog_entries += stream.generate_catalog()
        return catalog_entries

    @classmethod
    def _make_selected_catalog(cls, stream_names=None):
        """Build a catalog dict with ``selected=True`` for *stream_names*
        (default: all)."""
        raw_entries = cls._run_discover()
        streams = []

        for entry_dict in raw_entries:
            is_sel = (stream_names is None
                      or entry_dict['tap_stream_id'] in stream_names)

            mdata = metadata.to_map(entry_dict['metadata'])
            mdata = metadata.write(mdata, (), 'selected', is_sel)

            for field_name in entry_dict['schema'].get('properties', {}):
                mdata = metadata.write(
                    mdata, ('properties', field_name),
                    'selected', is_sel)

            entry_dict['metadata'] = metadata.to_list(mdata)
            streams.append(entry_dict)

        return {'streams': streams}

    @classmethod
    def _make_automatic_fields_catalog(cls, stream_names=None):
        """Build a catalog dict with only automatic (PK + replication key)
        fields selected."""
        raw_entries = cls._run_discover()
        expected = cls.expected_metadata()
        streams = []

        for entry_dict in raw_entries:
            is_sel = (stream_names is None
                      or entry_dict['tap_stream_id'] in stream_names)

            pk_fields = expected.get(
                entry_dict['tap_stream_id'], {}).get(
                    cls.PRIMARY_KEYS, set())

            mdata = metadata.to_map(entry_dict['metadata'])
            mdata = metadata.write(mdata, (), 'selected', is_sel)

            for field_name in entry_dict['schema'].get('properties', {}):
                mdata = metadata.write(
                    mdata, ('properties', field_name),
                    'selected', field_name in pk_fields)

            entry_dict['metadata'] = metadata.to_list(mdata)
            streams.append(entry_dict)

        return {'streams': streams}

    # ------------------------------------------------------------------ #
    #  Sync runner
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_sync(cls, catalog, state=None, client=None):
        """Run sync using real tap code with the given (mock) client."""
        config = dict(cls.default_config)
        if state is None:
            state = {}
        if client is None:
            client = cls._create_mock_client()

        streams = tap_uservoice.get_streams_to_replicate(
            config, state, catalog, client)

        for stream in streams:
            stream.state = state
            stream.sync()
            state = stream.state

        return state
