from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class ProductAreasStream(BaseStream):

    API_PATH = '/api/v2/admin/product_areas'
    TABLE = 'product_areas'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "name": {"type": ["string", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "updated_by": {"type": ["integer", "null"]},
                    "created_by": {"type": ["integer", "null"]}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('product_areas')
