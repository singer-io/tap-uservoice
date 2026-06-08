"""Integration test: pagination -- verify multi-page responses are fully
consumed via cursor-based pagination."""
import unittest
from unittest.mock import patch

from .base import UservoiceMockBaseTest


class PaginationIntegrationTest(UservoiceMockBaseTest, unittest.TestCase):
    """Test that streams with pagination fetch all pages of results."""

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_paginated_stream_fetches_all_pages(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Cursor-paginated streams should fetch records from all pages."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        client = self._create_paginated_mock_client()
        self._run_sync(catalog, client=client)

        all_records = []
        for call_args in mock_write_record.call_args_list:
            if call_args[0][0] == 'categories':
                all_records.append(call_args[0][1])

        # The tap syncs in 7-day windows from start_date to now.
        # Each window gets 2 pages of 1 record each, so total records
        # should be even (2 per window).
        self.assertTrue(len(all_records) > 0)
        self.assertEqual(len(all_records) % 2, 0,
                         "Paginated sync should return even record count (2 per window)")
        ids = {r['id'] for r in all_records}
        # Page 1 (seed=0) and page 2 (seed=10) produce different ids
        self.assertEqual(len(ids), 2, "Should have records from 2 different page seeds")

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_paginated_make_fetch_called_multiple_times(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """For a 2-page stream, fetch_data should be called at least twice."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        client = self._create_paginated_mock_client()
        self._run_sync(catalog, client=client)

        # Should have been called at least twice for categories
        categories_calls = [
            c for c in client.fetch_data.call_args_list
            if c[1].get('endpoint') == 'categories' or
            (len(c[0]) > 0 and 'categories' in str(c))
        ]
        self.assertGreaterEqual(len(categories_calls), 2)
