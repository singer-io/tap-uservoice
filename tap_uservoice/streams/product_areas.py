from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class ProductAreasStream(BaseStream):

    API_PATH = '/api/v2/admin/product_areas'
    TABLE = 'product_areas'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('product_areas')
