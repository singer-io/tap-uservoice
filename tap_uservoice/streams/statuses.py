from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class StatusesStream(BaseStream):

    API_PATH = '/api/v2/admin/statuses'
    TABLE = 'statuses'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": "integer"},
            "name": {"type": ["null", "string"]},
            "is_open": {"type": ["boolean", "null"]},
            "hex_color": {"type": ["string", "null"]},
            "position": {"type": ["integer", "null"]},
            "allow_comments": {"type": ["boolean", "null"]},
        }))

    def get_stream_data(self, result):
        return result.get('statuses')
