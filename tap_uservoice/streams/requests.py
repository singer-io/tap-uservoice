from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class RequestsStream(BaseStream):

    API_PATH = '/api/v2/admin/requests'
    TABLE = 'requests'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "body": {"type": ["string", "null"]},
            "body_mime_type": {"type": ["string", "null"]},
            "source_url": {"type": ["string", "null"]},
            "source_type": {"type": ["string", "null"]},
            "source_guid": {"type": ["string", "null"]},
            "channel": {"type": ["string", "null"]},
            "severity": {"type": ["integer", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "suggestion": {"type": ["integer", "null"]},
                    "user": {"type": ["integer", "null"]},
                    "ticket": {"type": ["integer", "null"]},
                    "created_by": {"type": ["integer", "null"]},
                    "updated_by": {"type": ["integer", "null"]},
                    "supporter": {"type": ["integer", "null"]},
                    "sfdc_opportunity": {"type": ["integer", "null"]}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('requests')
