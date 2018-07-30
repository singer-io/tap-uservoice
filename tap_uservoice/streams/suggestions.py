from funcy import merge

from tap_uservoice.schemas import with_properties, \
    DEFAULT_DATE_FIELDS, make_date_field
from tap_uservoice.streams.base import BaseStream


class SuggestionsStream(BaseStream):

    API_PATH = '/api/v2/admin/suggestions'
    TABLE = 'suggestions'
    SCHEMA = with_properties(merge(
        DEFAULT_DATE_FIELDS,
        make_date_field('approved_at'),
        make_date_field('closed_at'),
        make_date_field('first_support_at'),
        {
            "admin_url": {"type": "string"},
            "average_engagement": {"type": "number"},
            "body": {"type": "string"},
            "body_mime_type": {"type": "string"},
            "channel": {"type": "string"},
            "comments_count": {"type": "integer"},
            "creator_browser": {"type": ["string", "null"]},
            "creator_browser_version": {"type": ["string", "null"]},
            "creator_mobile": {"type": ["boolean", "null"]},
            "creator_os": {"type": ["string", "null"]},
            "creator_referrer": {"type": ["string", "null"]},
            "creator_user_agent": {"type": ["string", "null"]},
            "engagement_trend": {"type": "number"},
            "id": {"type": "integer"},
            "inappropriate_flags_count": {"type": "integer"},
            "is_blocker": {"type": ["boolean", "null"]},
            "notes_count": {"type": "integer"},
            "portal_url": {"type": "string"},
            "recent_engagement": {"type": "integer"},
            "requests_count": {"type": "integer"},
            "satisfaction_detractor_count": {"type": "integer"},
            "satisfaction_neutral_count": {"type": "integer"},
            "satisfaction_promoter_count": {"type": "integer"},
            "state": {"type": "string"},
            "supporter_mrr": {"type": "number"},
            "supporter_satisfaction_score": {"type": "number"},
            "supporters_count": {"type": "integer"},
            "supporting_accounts_count": {"type": "integer"},
            "title": {"type": "string"},
            "votes_count": {"type": "integer"},
            "links": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "category": {"type": ["integer", "null"]},
                    "created_by": {"type": ["integer", "null"]},
                    "forum": {"type": ["integer", "null"]},
                    "labels": {
                        "type": ["array", "null"],
                        "items": {
                            "type": ["integer", "null"]
                        }
                    },
                    "last_status_update": {"type": ["integer", "null"]},
                    "parent_suggestion": {"type": ["integer", "null"]},
                    "parent_suggestions": {
                        "type": ["array", "null"],
                        "items": {
                            "type": ["integer", "null"]
                        }
                    },
                    "status": {"type": ["integer", "null"]},
                    "ticket": {"type": ["integer", "null"]}
                }
            }
        }), additional=True)

    def get_stream_data(self, result):
        return result.get('suggestions')
