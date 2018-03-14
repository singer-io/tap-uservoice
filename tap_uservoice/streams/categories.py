from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class CategoriesStream(BaseStream):

    API_PATH = '/api/v2/admin/categories'
    TABLE = 'categories'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
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
            "links": {
                "type": "object",
                "properties": {
                    "forum": {
                        "type": "integer"
                    }
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('categories')
