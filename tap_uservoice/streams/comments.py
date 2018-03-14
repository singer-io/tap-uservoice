from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class CommentsStream(BaseStream):

    API_PATH = '/api/v2/admin/comments'
    TABLE = 'comments'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": "integer"},
            "body": {"type": "string"},
            "body_mime_type": {"type": "string"},
            "state": {"type": "string"},
            "inappropriate_flags_count": {"type": "integer"},
            "is_admin_comment": {"type": "boolean"},
            "channel": {"type": "string"},
            "links": {
                "type": "object",
                "properties": {
                    "suggestion": {"type": "integer"},
                    "created_by": {"type": "integer"}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('comments')
