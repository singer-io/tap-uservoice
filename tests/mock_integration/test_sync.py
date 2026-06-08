"""Integration test: do_sync() end-to-end pipeline writes schemas,
records, and state correctly."""
import unittest
from unittest.mock import patch

from .base import UservoiceMockBaseTest


class DoSyncIntegrationTest(UservoiceMockBaseTest, unittest.TestCase):

    def setUp(self):
        self.catalog = self._make_selected_catalog()

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_full_pipeline_emits_schemas_and_records(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """sync should emit SCHEMA then RECORD for each synced stream."""
        self._run_sync(self.catalog)

        schema_streams = {c[0][0] for c in mock_write_schema.call_args_list}
        record_streams = {c[0][0] for c in mock_write_record.call_args_list}

        for stream_name in self.ALL_STREAM_IDS:
            self.assertIn(stream_name, schema_streams,
                          f"Schema not emitted for {stream_name}")
            self.assertIn(stream_name, record_streams,
                          f"Records not written for {stream_name}")

    # ------------------------------------------------------------------
    # Schema emission order
    # ------------------------------------------------------------------

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_schema_emitted_before_records(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """For each stream, write_schema must be called before write_record."""
        call_order = []
        mock_write_schema.side_effect = lambda *a, **k: call_order.append(('schema', a[0]))
        mock_write_record.side_effect = lambda *a, **k: call_order.append(('record', a[0]))

        self._run_sync(self.catalog)

        for stream_name in self.ALL_STREAM_IDS:
            schema_indices = [
                i for i, (t, s) in enumerate(call_order)
                if t == 'schema' and s == stream_name
            ]
            record_indices = [
                i for i, (t, s) in enumerate(call_order)
                if t == 'record' and s == stream_name
            ]
            if schema_indices and record_indices:
                self.assertLess(
                    schema_indices[0], record_indices[0],
                    f"Schema for {stream_name} must come before its records",
                )

    # ------------------------------------------------------------------
    # Stream selection
    # ------------------------------------------------------------------

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_only_selected_streams_are_synced(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """When only 'categories' is selected, other streams are skipped."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        self._run_sync(catalog)

        record_streams = {c[0][0] for c in mock_write_record.call_args_list}
        self.assertIn('categories', record_streams)
        self.assertNotIn('comments', record_streams)
        self.assertNotIn('users', record_streams)

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_no_streams_selected_writes_nothing(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """When no streams are selected, nothing is written."""
        catalog = self._make_selected_catalog(stream_names=[])
        self._run_sync(catalog)

        mock_write_record.assert_not_called()

    # ------------------------------------------------------------------
    # Record field correctness
    # ------------------------------------------------------------------

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_records_have_correct_types(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Records have properly typed id field."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        self._run_sync(catalog)

        for call_args in mock_write_record.call_args_list:
            if call_args[0][0] == 'categories':
                record = call_args[0][1]
                self.assertIsInstance(record['id'], int)
                return
        self.fail("No categories records written")
