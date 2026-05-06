import unittest
from unittest.mock import Mock

from tap_uservoice.streams.base import BaseStream
from tap_uservoice.streams import AVAILABLE_STREAMS

from tap_uservoice.streams.categories import CategoriesStream
from tap_uservoice.streams.comments import CommentsStream
from tap_uservoice.streams.suggestions import SuggestionsStream
from tap_uservoice.streams.users import UsersStream
from tap_uservoice.streams.forums import ForumsStream
from tap_uservoice.streams.features import FeaturesStream
from tap_uservoice.streams.teams import TeamsStream


class TestCatalogProperties(unittest.TestCase):

    def setUp(self):
        self.config = {'subdomain': 'test', 'api_key': 'key', 'api_secret': 'secret'}
        self.state = {}
        self.catalog = None
        self.client = Mock()

    def test_base_stream_default_properties(self):
        """Test that BaseStream has the expected default properties."""
        self.assertEqual(BaseStream.KEY_PROPERTIES, ['id'])
        self.assertEqual(BaseStream.REPLICATION_KEY, 'updated_at')
        self.assertEqual(BaseStream.TABLE, None)
        self.assertEqual(BaseStream.REPLICATION_METHOD, 'INCREMENTAL')

    def test_categories_stream_properties(self):
        """Test that CategoriesStream has correct properties."""
        stream = CategoriesStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'categories')
        self.assertEqual(stream.API_PATH, '/api/v2/admin/categories')

    def test_comments_stream_properties(self):
        """Test that CommentsStream has correct properties."""
        stream = CommentsStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'comments')

    def test_suggestions_stream_properties(self):
        """Test that SuggestionsStream has correct properties."""
        stream = SuggestionsStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'suggestions')

    def test_users_stream_properties(self):
        """Test that UsersStream has correct properties."""
        stream = UsersStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'users')

    def test_forums_stream_properties(self):
        """Test that ForumsStream has correct properties."""
        stream = ForumsStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'forums')

    def test_features_stream_properties(self):
        """Test that FeaturesStream has correct properties."""
        stream = FeaturesStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'features')

    def test_teams_stream_properties(self):
        """Test that TeamsStream has correct properties."""
        stream = TeamsStream(self.config, self.state, self.catalog, self.client)
        self.assertEqual(stream.KEY_PROPERTIES, ['id'])
        self.assertEqual(stream.TABLE, 'teams')

    def test_all_streams_have_key_properties(self):
        """Test that all available streams have KEY_PROPERTIES defined."""
        for stream_class in AVAILABLE_STREAMS:
            with self.subTest(stream_class=stream_class.__name__):
                stream = stream_class(self.config, self.state, self.catalog, self.client)
                self.assertIsNotNone(stream.KEY_PROPERTIES)
                self.assertIsInstance(stream.KEY_PROPERTIES, list)
                self.assertGreater(len(stream.KEY_PROPERTIES), 0)

    def test_all_streams_have_table(self):
        """Every stream class should have a TABLE attribute."""
        for stream_cls in AVAILABLE_STREAMS:
            self.assertIsNotNone(stream_cls.TABLE,
                                 f"{stream_cls.__name__} missing TABLE")

    def test_all_streams_have_schema(self):
        """Every stream class should have a SCHEMA attribute."""
        for stream_cls in AVAILABLE_STREAMS:
            self.assertIsNotNone(stream_cls.SCHEMA,
                                 f"{stream_cls.__name__} missing SCHEMA")

    def test_all_streams_have_api_path(self):
        """Every stream class should have an API_PATH attribute."""
        for stream_cls in AVAILABLE_STREAMS:
            self.assertTrue(hasattr(stream_cls, 'API_PATH'),
                            f"{stream_cls.__name__} missing API_PATH")
            self.assertIsNotNone(stream_cls.API_PATH,
                                 f"{stream_cls.__name__} API_PATH is None")

    def test_replication_method_is_incremental(self):
        """Test that all streams use INCREMENTAL replication."""
        for stream_class in AVAILABLE_STREAMS:
            with self.subTest(stream_class=stream_class.__name__):
                stream = stream_class(self.config, self.state, self.catalog, self.client)
                self.assertEqual(stream.REPLICATION_METHOD, 'INCREMENTAL')

    def test_replication_key_is_updated_at(self):
        """Test that all streams use updated_at as replication key."""
        for stream_class in AVAILABLE_STREAMS:
            with self.subTest(stream_class=stream_class.__name__):
                stream = stream_class(self.config, self.state, self.catalog, self.client)
                self.assertEqual(stream.REPLICATION_KEY, 'updated_at')

    def test_matches_catalog(self):
        """Test that matches_catalog works correctly."""
        self.assertTrue(CategoriesStream.matches_catalog({'stream': 'categories'}))
        self.assertFalse(CategoriesStream.matches_catalog({'stream': 'comments'}))

    def test_catalog_structure_consistency(self):
        """Test that catalog generation produces consistent structure for all streams."""
        for stream_class in AVAILABLE_STREAMS:
            with self.subTest(stream_class=stream_class.__name__):
                stream = stream_class(self.config, self.state, self.catalog, self.client)
                catalog = stream.generate_catalog()

                self.assertEqual(len(catalog), 1)
                catalog_entry = catalog[0]

                required_fields = ['tap_stream_id', 'stream', 'key_properties', 'schema', 'metadata']
                for field in required_fields:
                    self.assertIn(field, catalog_entry)

                self.assertEqual(catalog_entry['tap_stream_id'], stream.TABLE)
                self.assertEqual(catalog_entry['stream'], stream.TABLE)
                self.assertEqual(catalog_entry['key_properties'], stream.KEY_PROPERTIES)
                self.assertIsInstance(catalog_entry['metadata'], list)


if __name__ == '__main__':
    unittest.main()
