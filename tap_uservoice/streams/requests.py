from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class RequestsStream(BaseStream):

    API_PATH = '/api/v2/admin/requests'
    TABLE = 'requests'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('requests')
