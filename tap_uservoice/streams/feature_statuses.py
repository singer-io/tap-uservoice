from tap_uservoice.schemas import with_properties
from tap_uservoice.streams.base import BaseStream


class FeatureStatusesStream(BaseStream):

    API_PATH = '/api/v2/admin/feature_statuses'
    TABLE = 'feature_statuses'
    SCHEMA = None

    def get_stream_data(self, result):
        return result.get('feature_statuses')
