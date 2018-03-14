from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class TeamsStream(BaseStream):

    API_PATH = '/api/v2/admin/teams'
    TABLE = 'teams'
    SCHEMA = with_properties({
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "members_count": {"type": "integer"},
    })

    def get_stream_data(self, result):
        return result.get('teams')
