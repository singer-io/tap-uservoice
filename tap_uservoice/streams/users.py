from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS, make_date_field
from tap_uservoice.streams.base import BaseStream


class UsersStream(BaseStream):

    API_PATH = '/api/v2/admin/users'
    TABLE = 'users'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        make_date_field('last_login'),
        {
            "id": {"type": "integer"},
            "guid": {"type": ["string", "null"]},
            "name": {"type": ["string", "null"]},
            "email_address": {"type": ["string", "null"]},
            "job_title": {"type": ["string", "null"]},
            "avatar_url": {"type": ["string", "null"]},
            "last_ip": {"type": ["string", "null"]},
            "country": {"type": ["string", "null"]},
            "region": {"type": ["string", "null"]},
            "city": {"type": ["string", "null"]},
            "satisfaction_score": {"type": ["integer", "null"]},
            "allowed_state": {"type": ["string", "null"]},
            "state": {"type": ["string", "null"]},
            "supported_suggestions_count": {"type": "integer"},
            "is_admin": {"type": "boolean"},
            "is_owner": {"type": "boolean"},
            "email_confirmed": {"type": "boolean"},
            "status_notifications": {"type": "boolean"},
            "comment_notifications": {"type": "boolean"},
            "links": {
                "type": "object",
                "properties": {
                    # todo: check these
                    "teams": {
                        "type": ["array", "null"],
                        "items": {
                            "type": ["integer", "null"]
                        }
                    },
                    "current_nps_rating": {"type": ["integer", "null"]},
                    "previous_nps_rating": {"type": ["integer", "null"]},
                    "external_users": {
                        "type": ["array", "null"],
                        "items": {
                            "type": ["integer", "null"]
                        }
                    }
                }
            }
        }))

    def get_stream_data(self, result):
        return result.get('users')
