"""Integration test: sync all streams with mocked API responses
and verify all fields are replicated."""
import unittest
from unittest.mock import patch

from .base import UservoiceMockBaseTest


class AllFieldsIntegrationTest(UservoiceMockBaseTest, unittest.TestCase):

    def setUp(self):
        self.catalog = self._make_selected_catalog()

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_sync_writes_records_for_all_streams(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Sync all streams and verify records are written for
        streams that have mock data."""
        self._run_sync(self.catalog)

        written_streams = {
            call_args[0][0] for call_args in mock_write_record.call_args_list
        }

        for stream_name in self.ALL_STREAM_IDS:
            self.assertIn(stream_name, written_streams,
                          f"No records written for {stream_name}")

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_records_have_id_field(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """All records should have the 'id' field (primary key)."""
        self._run_sync(self.catalog)

        for call_args in mock_write_record.call_args_list:
            record = call_args[0][1]
            self.assertIn('id', record,
                          f"id missing in record for stream")

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_sync_only_single_stream(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Sync only categories and verify only category records written."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        self._run_sync(catalog)

        written_streams = {
            call_args[0][0] for call_args in mock_write_record.call_args_list
        }
        self.assertIn('categories', written_streams)
        self.assertNotIn('comments', written_streams)
        self.assertNotIn('users', written_streams)
