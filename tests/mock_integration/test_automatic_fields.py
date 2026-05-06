"""Integration test: with only automatic (primary-key) fields selected,
verify those fields still appear in every replicated record."""
import unittest
from unittest.mock import patch

from .base import UservoiceMockBaseTest


class AutomaticFieldsIntegrationTest(UservoiceMockBaseTest, unittest.TestCase):
    """Test that with no fields selected for a stream, automatic fields
    (primary keys) are still replicated."""

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_automatic_fields_present_for_all_streams(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """When only automatic fields are selected, every record still
        contains the primary key fields for its stream."""
        catalog = self._make_automatic_fields_catalog()
        self._run_sync(catalog)

        expected = self.expected_metadata()
        written = {}
        for call_args in mock_write_record.call_args_list:
            stream_name = call_args[0][0]
            record = call_args[0][1]
            written.setdefault(stream_name, []).append(record)

        for stream_name, records in written.items():
            pk_fields = expected[stream_name][self.PRIMARY_KEYS]
            for record in records:
                for pk in pk_fields:
                    self.assertIn(
                        pk, record,
                        f"Primary key '{pk}' missing in {stream_name} record",
                    )

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_automatic_fields_single_stream(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Automatic fields test for categories stream only."""
        catalog = self._make_automatic_fields_catalog(
            stream_names=['categories'])
        self._run_sync(catalog)

        for call_args in mock_write_record.call_args_list:
            if call_args[0][0] == 'categories':
                record = call_args[0][1]
                self.assertIn('id', record)
                return
        self.fail("No categories records written")

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_schema_emitted_with_automatic_fields_only(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Schemas are still emitted even when only automatic fields selected."""
        catalog = self._make_automatic_fields_catalog()
        self._run_sync(catalog)

        schema_streams = {c[0][0] for c in mock_write_schema.call_args_list}
        for stream_name in self.ALL_STREAM_IDS:
            self.assertIn(stream_name, schema_streams,
                          f"Schema not emitted for {stream_name}")
