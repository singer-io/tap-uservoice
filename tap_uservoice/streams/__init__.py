from tap_uservoice.streams.categories import CategoriesStream
from tap_uservoice.streams.comments import CommentsStream
from tap_uservoice.streams.external_accounts \
    import ExternalAccountsStream
from tap_uservoice.streams.external_users import ExternalUsersStream
from tap_uservoice.streams.feature_statuses import FeatureStatusesStream
from tap_uservoice.streams.features import FeaturesStream
from tap_uservoice.streams.forums import ForumsStream
from tap_uservoice.streams.labels import LabelsStream
from tap_uservoice.streams.nps_ratings import NpsRatingsStream
from tap_uservoice.streams.product_areas import ProductAreasStream
from tap_uservoice.streams.requests import RequestsStream
from tap_uservoice.streams.segmented_values import SegmentedValuesStream
from tap_uservoice.streams.segments import SegmentsStream
from tap_uservoice.streams.status_updates import StatusUpdatesStream
from tap_uservoice.streams.statuses import StatusesStream
from tap_uservoice.streams.suggestions import SuggestionsStream
from tap_uservoice.streams.supporters import SupportersStream
from tap_uservoice.streams.teams import TeamsStream
from tap_uservoice.streams.users import UsersStream

__all__ = AVAILABLE_STREAMS = [
    CategoriesStream,
    CommentsStream,
    ExternalAccountsStream,
    ExternalUsersStream,
    FeatureStatusesStream,
    FeaturesStream,
    ForumsStream,
    LabelsStream,
    NpsRatingsStream,
    ProductAreasStream,
    RequestsStream,
    SegmentedValuesStream,
    SegmentsStream,
    StatusUpdatesStream,
    StatusesStream,
    SuggestionsStream,
    SupportersStream,
    TeamsStream,
    UsersStream,
]
