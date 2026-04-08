import unittest
from unittest.mock import Mock

from tap_uservoice.streams.base import BaseStream
from tap_uservoice.streams import AVAILABLE_STREAMS


EXPECTED_STREAMS = {
    'categories', 'comments', 'external_accounts', 'external_users',
    'feature_statuses', 'features', 'forums', 'labels', 'nps_ratings',
    'product_areas', 'requests', 'segmented_values', 'segments',
    'status_updates', 'statuses', 'suggestions', 'supporters',
    'teams', 'users',
}


class TestCatalogGeneration(unittest.TestCase):
    """Test that catalog / discover output is valid."""

    def test_expected_streams_match_available_streams(self):
        """AVAILABLE_STREAMS should contain exactly the expected streams."""
        actual = {s.TABLE for s in AVAILABLE_STREAMS}
        self.assertEqual(actual, EXPECTED_STREAMS)

    def test_generate_catalog_returns_correct_structure(self):
        """generate_catalog should return list of dicts with required keys."""
        for stream_cls in AVAILABLE_STREAMS:
            inst = stream_cls({}, {}, None, None)
            catalog = inst.generate_catalog()
            self.assertIsInstance(catalog, list)
            for entry in catalog:
                self.assertIn('tap_stream_id', entry)
                self.assertIn('stream', entry)
                self.assertIn('key_properties', entry)
                self.assertIn('schema', entry)
                self.assertIn('metadata', entry)
                self.assertEqual(entry['tap_stream_id'], stream_cls.TABLE)
                self.assertEqual(entry['key_properties'], stream_cls.KEY_PROPERTIES)

    def test_schema_has_properties(self):
        """Each stream schema should have 'properties' key."""
        for stream_cls in AVAILABLE_STREAMS:
            with self.subTest(stream=stream_cls.TABLE):
                schema = stream_cls.SCHEMA
                self.assertIn('properties', schema)
                self.assertTrue(len(schema['properties']) > 0)

    def test_key_properties_in_schema(self):
        """All KEY_PROPERTIES should exist in the stream's schema."""
        for stream_cls in AVAILABLE_STREAMS:
            with self.subTest(stream=stream_cls.TABLE):
                schema_fields = set(stream_cls.SCHEMA.get('properties', {}).keys())
                for key in stream_cls.KEY_PROPERTIES:
                    self.assertIn(
                        key, schema_fields,
                        f'{stream_cls.TABLE}: KEY_PROPERTY "{key}" not in schema')

    def test_metadata_has_automatic_for_key_properties(self):
        """Key properties should have inclusion=automatic in metadata."""
        for stream_cls in AVAILABLE_STREAMS:
            inst = stream_cls({}, {}, None, None)
            catalog = inst.generate_catalog()
            for entry in catalog:
                metadata_map = {
                    tuple(m['breadcrumb']): m['metadata']
                    for m in entry['metadata']
                }
                for key_prop in stream_cls.KEY_PROPERTIES:
                    breadcrumb = ('properties', key_prop)
                    self.assertIn(breadcrumb, metadata_map,
                                  f'{stream_cls.TABLE}: missing metadata for {key_prop}')
                    self.assertEqual(
                        metadata_map[breadcrumb].get('inclusion'), 'automatic',
                        f'{stream_cls.TABLE}: {key_prop} should be automatic')

    def test_replication_key_has_automatic_inclusion(self):
        """Replication key should have inclusion=automatic in metadata."""
        for stream_cls in AVAILABLE_STREAMS:
            if stream_cls.REPLICATION_KEY is None:
                continue
            inst = stream_cls({}, {}, None, None)
            catalog = inst.generate_catalog()
            for entry in catalog:
                metadata_map = {
                    tuple(m['breadcrumb']): m['metadata']
                    for m in entry['metadata']
                }
                breadcrumb = ('properties', stream_cls.REPLICATION_KEY)
                if breadcrumb in metadata_map:
                    self.assertEqual(
                        metadata_map[breadcrumb].get('inclusion'), 'automatic',
                        f'{stream_cls.TABLE}: {stream_cls.REPLICATION_KEY} should be automatic')


if __name__ == '__main__':
    unittest.main()
