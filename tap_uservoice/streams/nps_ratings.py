from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class NpsRatingsStream(BaseStream):

    API_PATH = '/api/v2/admin/nps_ratings'
    TABLE = 'nps_ratings'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "rating": {"type": ["integer", "null"]},
            "previous_rating": {"type": ["integer", "null"]},
            "rating_delta": {"type": ["integer", "null"]},
            "body": {"type": ["string", "null"]},
            "prompt": {"type": ["string", "null"]},
            "group": {"type": ["string", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "user": {"type": ["integer", "null"]},
                    "ticket": {"type": ["integer", "null"]}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('nps_ratings')
