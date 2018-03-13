from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class SuggestionsStream(BaseStream):

    API_PATH = '/api/v2/admin/suggestions'
    TABLE = 'suggestions'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('suggestions')
