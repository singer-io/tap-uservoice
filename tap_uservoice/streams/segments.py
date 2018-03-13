from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class SegmentsStream(BaseStream):

    API_PATH = '/api/v2/admin/segments'
    TABLE = 'segments'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('segments')
