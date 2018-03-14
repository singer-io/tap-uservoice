from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class SegmentsStream(BaseStream):

    API_PATH = '/api/v2/admin/segments'
    TABLE = 'segments'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "key": {"type": ["string", "null"]},
            "name": {"type": ["string", "null"]},
            "filters": {
                "type": "object",
                "additionalProperties": True
            }
        }))

    def get_stream_data(self, result):
        return result.get('segments')
