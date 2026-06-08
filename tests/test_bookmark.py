from base import UservoiceBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class UservoiceBookmarkTest(BookmarkTest, UservoiceBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%SZ"
    initial_bookmarks = {}

    @staticmethod
    def name():
        return "tap_tester_uservoice_bookmark_test"

    def streams_to_test(self):
        return self.expected_stream_names()
