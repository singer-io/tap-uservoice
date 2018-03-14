from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class SupportersStream(BaseStream):

    API_PATH = '/api/v2/admin/supporters'
    TABLE = 'supporters'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": "integer"},
            "is_subscribed": {"type": "boolean"},
            "how": {"type": "string"},
            "channel": {"type": "string"},
            "requests_count": {"type": "integer"},
            "comments_count": {"type": "integer"},
            "links": {
                "type": "object",
                "properties": {
                    "suggestion": {"type": "integer"},
                    "user": {"type": "integer"},
                    "created_by": {"type": "integer"},
                    "updated_by": {"type": "integer"},
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('supporters')
