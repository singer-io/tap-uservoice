from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class ExternalAccountsStream(BaseStream):

    API_PATH = '/api/v2/admin/external_accounts'
    TABLE = 'external_accounts'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('external_accounts')
