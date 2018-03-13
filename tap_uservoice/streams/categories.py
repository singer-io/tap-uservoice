from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class CategoriesStream(BaseStream):

    API_PATH = '/api/v2/admin/categories'
    TABLE = 'categories'
    SCHEMA = with_properties({
        "id": {
            "type": "integer"
        },
        "name": {
            "type": "string"
        },
        "suggestions_count": {
            "type": "integer",
        },
        "open_suggestions_count": {
            "type": "integer",
        },
        "created_at": {
            "type": "string",
            "format": "date-time"
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
        },
        "links": {
            "type": "object",
            "properties": {
                "forum": {
                    "type": "integer"
                }
            }
        }
    })

    def get_stream_data(self, result):
        return result.get('categories')
