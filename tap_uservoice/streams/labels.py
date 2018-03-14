from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class LabelsStream(BaseStream):

    API_PATH = '/api/v2/admin/labels'
    TABLE = 'labels'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "name": {"type": ["string", "null"]},
            "full_name": {"type": ["string", "null"]},
            "level": {"type": ["integer", "null"]},
            "open_suggestions_count": {"type": ["integer", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "parent": {"type": ["integer", "null"]}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('labels')
