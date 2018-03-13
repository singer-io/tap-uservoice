from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class SegmentedValuesStream(BaseStream):

    API_PATH = '/api/v2/admin/segmented_values'
    TABLE = 'segmented_values'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('segmented_values')
