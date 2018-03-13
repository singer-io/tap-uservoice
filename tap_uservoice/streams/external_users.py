from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class ExternalUsersStream(BaseStream):

    API_PATH = '/api/v2/admin/external_users'
    TABLE = 'external_users'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('external_users')
