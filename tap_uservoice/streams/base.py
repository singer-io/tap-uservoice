import pytz
import singer

from datetime import timedelta, datetime
from funcy import project
from tap_uservoice.config import get_config_start_date
from tap_uservoice.state import incorporate, save_state, \
    get_last_record_value_for_table

LOGGER = singer.get_logger()


class BaseStream:

    # ABSTRACT PROPERTIES -- SHOULD BE OVERRIDDEN
    TABLE = None
    SCHEMA = None

    def get_stream_data(self, result):
        """
        Given a result set from Uservoice, return the data
        to be persisted for this stream.
        """
        raise RuntimeError("get_stream_data not implemented!")

    # GLOBAL PROPERTIES -- DON'T OVERRIDE
    KEY_PROPERTIES = ['id']

    def __init__(self, config, state, catalog, client):
        self.config = config
        self.state = state
        self.catalog = catalog
        self.client = client

    @classmethod
    def matches_catalog(cls, catalog):
        return catalog.get('stream') == cls.TABLE

    def generate_catalog(self):
        cls = self.__class__

        return [{
            'tap_stream_id': cls.TABLE,
            'stream': cls.TABLE,
            'key_properties': cls.KEY_PROPERTIES,
            'schema': cls.SCHEMA,
            'replication_key': 'updated_at'
        }]

    def get_catalog_keys(self):
        return list(
            self.catalog.get('schema', {}).get('properties', {}).keys())

    def filter_keys(self, obj):
        return project(obj, self.get_catalog_keys())

    def write_schema(self):
        singer.write_schema(
            self.catalog.get('stream'),
            self.catalog.get('schema'),
            key_properties=self.catalog.get('key_properties'))

    def sync(self):
        LOGGER.info('Syncing stream {} with {}'
                    .format(self.catalog.get('tap_stream_id'),
                            self.__class__.__name__))

        self.write_schema()

        return self.sync_data()

    def sync_data_for_date(self, date, interval):
        table = self.TABLE

        updated_after = date
        updated_before = updated_after + interval
        cursor = None
        has_data = True

        while has_data:
            url = 'https://{}.uservoice.com{}'.format(
                self.config.get('subdomain'),
                self.API_PATH)

            result = self.client.fetch_data(
                url, updated_after, updated_before, cursor)

            cursor = result.get('pagination', {}).get('cursor')
            data = self.get_stream_data(result)
            has_data = (data is not None) and (len(data) > 0)

            if has_data:
                for obj in data:
                    singer.write_records(
                        table,
                        self.filter_keys(obj))

                    self.state = incorporate(self.state,
                                             table,
                                             'updated_at',
                                             obj.get('updated_at'))

                if cursor is None:
                    raise RuntimeError('Found data, but there is no '
                                       'continuation cursor!')

            else:
                LOGGER.info('No data returned, moving on.')

        save_state(self.state)

    def sync_data(self):
        table = self.TABLE

        date = get_last_record_value_for_table(self.state, table)

        if date is None:
            date = get_config_start_date(self.config)

        interval = timedelta(days=1)

        while date < datetime.now(pytz.utc):
            self.sync_data_for_date(date, interval)

            date = date + interval
