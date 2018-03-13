from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class ForumsStream(BaseStream):

    API_PATH = '/api/v2/admin/forums'
    TABLE = 'forums'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('forums')
