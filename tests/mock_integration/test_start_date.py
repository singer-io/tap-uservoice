"""Integration test: start-date / bookmark resume -- verify that
incremental streams use bookmark dates and that a second sync with
prior state picks up where it left off."""
import unittest
from unittest.mock import patch

from .base import UservoiceMockBaseTest


class StartDateIntegrationTest(UservoiceMockBaseTest, unittest.TestCase):
    """Test that bookmarked state is used as a start_date on subsequent syncs."""

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_first_sync_uses_config_start_date(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """On first sync (no state), the config start_date is used."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        client = self._create_mock_client()
        self._run_sync(catalog, state={}, client=client)

        # fetch_data should have been called
        self.assertTrue(client.fetch_data.called)

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_second_sync_uses_bookmark(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """On second sync with existing bookmark, the bookmark date
        determines the start of the sync window."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        initial_state = {
            'bookmarks': {
                'categories': {
                    'field': 'updated_at',
                    'last_record': self.get_initial_bookmark_date(),
                }
            }
        }
        client = self._create_date_filtering_mock_client()
        self._run_sync(catalog, state=initial_state, client=client)

        # fetch_data should have been called
        self.assertTrue(client.fetch_data.called)

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_bookmark_updated_after_sync(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Bookmark should be updated after sync."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        state = self._run_sync(catalog)

        bookmarks = state.get('bookmarks', {})
        bm = bookmarks.get('categories', {})
        self.assertIn('last_record', bm)
        self.assertIsNotNone(bm['last_record'])
