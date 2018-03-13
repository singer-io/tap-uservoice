from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class LabelsStream(BaseStream):

    API_PATH = '/api/v2/admin/labels'
    TABLE = 'labels'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('labels')
