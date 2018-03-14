from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS
from tap_uservoice.streams.base import BaseStream


class StatusUpdatesStream(BaseStream):

    API_PATH = '/api/v2/admin/status_updates'
    TABLE = 'status_updates'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        {
            "id": {"type": ["integer", "null"]},
            "body": {"type": ["string", "null"]},
            "supporters_notified": {"type": ["boolean", "null"]},
            "notification_email_address": {"type": ["string", "null"]},
            "mail_sent_count": {"type": ["integer", "null"]},
            "mail_opened_count": {"type": ["integer", "null"]},
            "mail_clicked_count": {"type": ["integer", "null"]},
            "links": {
                "type": "object",
                "properties": {
                    "suggestion": {"type": ["integer", "null"]},
                    "user": {"type": ["integer", "null"]},
                    "new_status": {"type": ["integer", "null"]},
                    "old_status": {"type": ["integer", "null"]}
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('status_updates')
