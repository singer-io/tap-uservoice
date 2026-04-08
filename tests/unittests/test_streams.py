import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz

from tap_uservoice.streams.base import BaseStream
from tap_uservoice.streams.categories import CategoriesStream
from tap_uservoice.streams.comments import CommentsStream
from tap_uservoice.streams.suggestions import SuggestionsStream
from tap_uservoice.streams.users import UsersStream
from tap_uservoice.streams.forums import ForumsStream
from tap_uservoice.streams import AVAILABLE_STREAMS


def _make_mock_client():
    """Create a mock client."""
    client = MagicMock()
    client.access_token = 'test_token'
    return client


def _make_catalog(stream_cls):
    """Create a catalog dict for the given stream class."""
    return {
        'tap_stream_id': stream_cls.TABLE,
        'stream': stream_cls.TABLE,
        'key_properties': stream_cls.KEY_PROPERTIES,
        'schema': stream_cls.SCHEMA,
        'metadata': stream_cls.load_metadata(stream_cls.SCHEMA),
    }


class TestStreamGetStreamData(unittest.TestCase):
    """Test get_stream_data for various stream types."""

    def test_categories_get_stream_data(self):
        """Test CategoriesStream.get_stream_data extracts categories."""
        stream = CategoriesStream({}, {}, None, None)
        result = {'categories': [{'id': 1, 'name': 'Test'}]}
        data = stream.get_stream_data(result)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 1)

    def test_comments_get_stream_data(self):
        """Test CommentsStream.get_stream_data extracts comments."""
        stream = CommentsStream({}, {}, None, None)
        result = {'comments': [{'id': 1, 'body': 'Test comment'}]}
        data = stream.get_stream_data(result)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['body'], 'Test comment')

    def test_suggestions_get_stream_data(self):
        """Test SuggestionsStream.get_stream_data extracts suggestions."""
        stream = SuggestionsStream({}, {}, None, None)
        result = {'suggestions': [{'id': 1, 'title': 'Test'}]}
        data = stream.get_stream_data(result)
        self.assertEqual(len(data), 1)

    def test_users_get_stream_data(self):
        """Test UsersStream.get_stream_data extracts users."""
        stream = UsersStream({}, {}, None, None)
        result = {'users': [{'id': 1, 'name': 'Test User'}]}
        data = stream.get_stream_data(result)
        self.assertEqual(len(data), 1)

    def test_forums_get_stream_data(self):
        """Test ForumsStream.get_stream_data extracts forums."""
        stream = ForumsStream({}, {}, None, None)
        result = {'forums': [{'id': 1, 'name': 'Test Forum'}]}
        data = stream.get_stream_data(result)
        self.assertEqual(len(data), 1)

    def test_get_stream_data_empty_result(self):
        """Test get_stream_data returns None for missing key."""
        stream = CategoriesStream({}, {}, None, None)
        result = {'other_key': []}
        data = stream.get_stream_data(result)
        self.assertIsNone(data)

    def test_all_streams_get_stream_data(self):
        """Test that all streams have a working get_stream_data."""
        for stream_cls in AVAILABLE_STREAMS:
            with self.subTest(stream=stream_cls.TABLE):
                stream = stream_cls({}, {}, None, None)
                result = {stream_cls.TABLE: [{'id': 1}]}
                data = stream.get_stream_data(result)
                self.assertIsNotNone(data)
                self.assertEqual(len(data), 1)


class TestStreamApiPath(unittest.TestCase):
    """Test API_PATH for various streams."""

    def test_categories_api_path(self):
        """Test CategoriesStream.API_PATH."""
        self.assertEqual(CategoriesStream.API_PATH, '/api/v2/admin/categories')

    def test_comments_api_path(self):
        """Test CommentsStream.API_PATH."""
        self.assertEqual(CommentsStream.API_PATH, '/api/v2/admin/comments')

    def test_suggestions_api_path(self):
        """Test SuggestionsStream.API_PATH."""
        self.assertEqual(SuggestionsStream.API_PATH, '/api/v2/admin/suggestions')

    def test_users_api_path(self):
        """Test UsersStream.API_PATH."""
        self.assertEqual(UsersStream.API_PATH, '/api/v2/admin/users')

    def test_forums_api_path(self):
        """Test ForumsStream.API_PATH."""
        self.assertEqual(ForumsStream.API_PATH, '/api/v2/admin/forums')

    def test_all_streams_api_path_starts_with_slash(self):
        """Test all streams have API_PATH starting with /."""
        for stream_cls in AVAILABLE_STREAMS:
            with self.subTest(stream=stream_cls.TABLE):
                self.assertTrue(
                    stream_cls.API_PATH.startswith('/'),
                    f"{stream_cls.__name__} API_PATH should start with /")


class TestBaseStreamSync(unittest.TestCase):
    """Test BaseStream sync logic."""

    @patch('tap_uservoice.streams.base.save_state')
    @patch('tap_uservoice.streams.base.singer.write_record')
    @patch('tap_uservoice.streams.base.singer.write_schema')
    @patch('tap_uservoice.streams.base.get_config_start_date')
    def test_sync_data_writes_records(self, mock_start_date, mock_write_schema,
                                       mock_write_record, mock_save_state):
        """Test that sync_data calls write_record for each data item."""
        mock_start_date.return_value = datetime.now(pytz.utc) - timedelta(days=1)

        client = _make_mock_client()
        client.fetch_data.return_value = {
            'categories': [
                {'id': 1, 'name': 'Test', 'updated_at': '2024-01-15T10:30:00Z',
                 'created_at': '2024-01-15T10:30:00Z'}
            ],
            'pagination': {'cursor': None, 'total_pages': 1}
        }

        catalog = _make_catalog(CategoriesStream)
        stream = CategoriesStream(
            config={'subdomain': 'test', 'start_date': '2024-01-01T00:00:00Z'},
            state={},
            catalog=catalog,
            client=client
        )
        stream.sync()
        mock_write_record.assert_called()

    @patch('tap_uservoice.streams.base.save_state')
    @patch('tap_uservoice.streams.base.singer.write_record')
    @patch('tap_uservoice.streams.base.singer.write_schema')
    @patch('tap_uservoice.streams.base.get_config_start_date')
    def test_sync_incorporates_bookmark(self, mock_start_date, mock_write_schema,
                                         mock_write_record, mock_save_state):
        """Test that sync updates bookmark state."""
        mock_start_date.return_value = datetime.now(pytz.utc) - timedelta(days=1)

        client = _make_mock_client()
        client.fetch_data.return_value = {
            'categories': [
                {'id': 1, 'name': 'Test', 'updated_at': '2024-06-15T10:30:00Z',
                 'created_at': '2024-01-15T10:30:00Z'}
            ],
            'pagination': {'cursor': None, 'total_pages': 1}
        }

        catalog = _make_catalog(CategoriesStream)
        stream = CategoriesStream(
            config={'subdomain': 'test', 'start_date': '2024-01-01T00:00:00Z'},
            state={},
            catalog=catalog,
            client=client
        )
        state = stream.sync()
        self.assertIn('bookmarks', state)
        mock_save_state.assert_called()

    @patch('tap_uservoice.streams.base.save_state')
    @patch('tap_uservoice.streams.base.singer.write_record')
    @patch('tap_uservoice.streams.base.singer.write_schema')
    @patch('tap_uservoice.streams.base.get_config_start_date')
    def test_sync_no_data_moves_on(self, mock_start_date, mock_write_schema,
                                    mock_write_record, mock_save_state):
        """Test that sync handles empty data gracefully."""
        mock_start_date.return_value = datetime.now(pytz.utc) - timedelta(days=1)

        client = _make_mock_client()
        client.fetch_data.return_value = {
            'categories': [],
            'pagination': {'cursor': None, 'total_pages': 0}
        }

        catalog = _make_catalog(CategoriesStream)
        stream = CategoriesStream(
            config={'subdomain': 'test', 'start_date': '2024-01-01T00:00:00Z'},
            state={},
            catalog=catalog,
            client=client
        )
        state = stream.sync()
        mock_write_record.assert_not_called()


class TestStreamProperties(unittest.TestCase):
    """Test stream class properties."""

    def test_all_streams_have_table(self):
        """Every stream class should have a TABLE attribute."""
        for stream_cls in AVAILABLE_STREAMS:
            self.assertIsNotNone(stream_cls.TABLE,
                                 f"{stream_cls.__name__} missing TABLE")

    def test_all_streams_have_key_properties(self):
        """Every stream class should have KEY_PROPERTIES."""
        for stream_cls in AVAILABLE_STREAMS:
            self.assertIsInstance(stream_cls.KEY_PROPERTIES, list,
                                 f"{stream_cls.__name__} KEY_PROPERTIES not a list")
            self.assertGreater(len(stream_cls.KEY_PROPERTIES), 0,
                               f"{stream_cls.__name__} has empty KEY_PROPERTIES")

    def test_all_streams_have_replication_key(self):
        """Every stream class should have a REPLICATION_KEY."""
        for stream_cls in AVAILABLE_STREAMS:
            self.assertEqual(stream_cls.REPLICATION_KEY, 'updated_at',
                             f"{stream_cls.__name__} should have updated_at as REPLICATION_KEY")


if __name__ == '__main__':
    unittest.main()
