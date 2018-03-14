from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class FeatureStatusesStream(BaseStream):

    API_PATH = '/api/v2/admin/feature_statuses'
    TABLE = 'feature_statuses'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "name": {"type": ["string", "null"]},
            "hex_color": {"type": ["string", "null"]},
            "position": {"type": ["integer", "null"]},
            "is_default": {"type": ["boolean", "null"]},
            "links": {
                "updated_by": {"type": ["integer", "null"]},
                "created_by": {"type": ["integer", "null"]}
            }
        }))

    def get_stream_data(self, result):
        return result.get('feature_statuses')
