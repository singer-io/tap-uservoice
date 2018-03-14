from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class ForumsStream(BaseStream):

    API_PATH = '/api/v2/admin/forums'
    TABLE = 'forums'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "name": {"type": ["string", "null"]},
            "welcome_message": {"type": ["string", "null"]},
            "welcome_message_mime_type": {"type": ["string", "null"]},
            "prompt": {"type": ["string", "null"]},
            "example": {"type": ["string", "null"]},
            "portal_url": {"type": ["string", "null"]},
            "open_suggestions_count": {"type": ["integer", "null"]},
            "suggestions_count": {"type": ["integer", "null"]},
            "category_required": {"type": ["boolean", "null"]},
            "is_public": {"type": ["boolean", "null"]},
            "is_private": {"type": ["boolean", "null"]},
            "classic_voting": {"type": ["boolean", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "updated_by": {"type": ["integer", "null"]}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('forums')
