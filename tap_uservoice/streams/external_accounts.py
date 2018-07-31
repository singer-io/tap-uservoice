from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS, make_date_field
from tap_uservoice.streams.base import BaseStream


class ExternalAccountsStream(BaseStream):

    API_PATH = '/api/v2/admin/external_accounts'
    TABLE = 'external_accounts'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        make_date_field('external_created_at'),
        make_date_field('last_active_at'),
        {
            "external_id": {"type": ["string", "null"]},
            "id": {"type": ["integer", "null"]},
            "is_blocker": {"type": ["boolean", "null"]},
            "ltv": {"type": ["number", "null"]},
            "ltv_cents": {"type": ["integer", "null"]},
            "mrr": {"type": ["number", "null"]},
            "mrr_cents": {"type": ["integer", "null"]},
            "name": {"type": ["string", "null"]},
            "nps": {"type": ["number", "null"]},
            "plan": {"type": ["string", "null"]},
            "requests_count": {"type": ["integer", "null"]},
            "supported_ideas_count": {"type": ["integer", "null"]},
            "users_count": {"type": ["integer", "null"]},
        }),
                             additional=True)

    def get_stream_data(self, result):
        return result.get('external_accounts')
