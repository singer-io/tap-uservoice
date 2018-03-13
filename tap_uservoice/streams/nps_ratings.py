from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class NpsRatingsStream(BaseStream):

    API_PATH = '/api/v2/admin/nps_ratings'
    TABLE = 'nps_ratings'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('nps_ratings')
