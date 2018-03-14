from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class FeaturesStream(BaseStream):

    API_PATH = '/api/v2/admin/features'
    TABLE = 'features'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "description": {"type": ["string", "null"]},
            "is_blocker": {"type": ["boolean", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "created_by": {"type": ["integer", "null"]},
                    "feature_status": {"type": ["integer", "null"]},
                    "product_area": {"type": ["integer", "null"]},
                    "updated_by": {"type": ["integer", "null"]}
                },
                "additionalProperties": True
            },
            "name": {"type": ["string", "null"]},
            "suggestions_count": {"type": ["integer", "null"]},
            "supporter_mrr_cents": {"type": ["integer", "null"]},
            "supporting_accounts_count": {"type": ["integer", "null"]},
            "supporting_users_count": {"type": ["integer", "null"]},
        }), additional=True)

    def get_stream_data(self, result):
        return result.get('features')
