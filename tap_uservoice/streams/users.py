from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class UsersStream(BaseStream):

    API_PATH = '/api/v2/admin/users'
    TABLE = 'users'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('users')
