from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS, make_date_field
from tap_uservoice.streams.base import BaseStream


class ExternalUsersStream(BaseStream):

    API_PATH = '/api/v2/admin/external_users'
    TABLE = 'external_users'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        make_date_field("external_created_at"),
        make_date_field("last_seen_at"),
        {
            "email": {"type": ["string", "null"]},
            "external_id": {"type": ["string", "null"]},
            "id": {"type": ["integer", "null"]},
            "ip": {"type": ["string", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "external_accounts": {"type": ["integer", "null"]},
                    "external_users": {"type": ["integer", "null"]},
                },
            },
            "name": {"type": ["string", "null"]},
            "seen_days": {"type": ["integer", "null"]},
            "type": {"type": ["string", "null"]},
        }),
                             additional=True)

    def get_stream_data(self, result):
        return result.get('external_users')
