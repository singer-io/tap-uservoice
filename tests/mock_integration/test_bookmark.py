"""Integration test: bookmark / state management for incremental streams."""
import unittest
from unittest.mock import patch

from .base import UservoiceMockBaseTest


class BookmarkIntegrationTest(UservoiceMockBaseTest, unittest.TestCase):

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_incremental_stream_updates_state(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Incremental streams should update state bookmarks with
        updated_at values."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        state = self._run_sync(catalog)

        bookmarks = state.get('bookmarks', {})
        self.assertIn('categories', bookmarks)
        bookmark = bookmarks['categories']
        self.assertEqual(bookmark.get('field'), 'updated_at')
        self.assertIsNotNone(bookmark.get('last_record'))

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_state_written_during_sync(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """write_state is called during sync to persist progress."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        self._run_sync(catalog)
        self.assertTrue(mock_write_state.called)

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_multiple_streams_each_get_bookmarks(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Multiple streams get their own bookmarks."""
        catalog = self._make_selected_catalog(
            stream_names=['categories', 'comments', 'forums'])
        state = self._run_sync(catalog)

        bookmarks = state.get('bookmarks', {})
        self.assertIn('categories', bookmarks)
        self.assertIn('comments', bookmarks)
        self.assertIn('forums', bookmarks)

    @patch("tap_uservoice.state.singer.write_state")
    @patch("singer.write_record")
    @patch("singer.write_schema")
    def test_bookmark_structure_has_field_and_last_record(
        self, mock_write_schema, mock_write_record, mock_write_state,
    ):
        """Bookmark entries should have 'field' and 'last_record' keys."""
        catalog = self._make_selected_catalog(stream_names=['categories'])
        state = self._run_sync(catalog)

        bookmarks = state.get('bookmarks', {})
        bm = bookmarks.get('categories', {})
        self.assertIn('field', bm)
        self.assertIn('last_record', bm)
        self.assertEqual(bm['field'], 'updated_at')
        self.assertIsInstance(bm['last_record'], str)
