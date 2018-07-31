from datetime import timedelta, datetime
import pytz
import singer
import singer.metrics

from singer import metadata
from singer import Transformer
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
    REPLICATION_KEY = 'updated_at'
    REPLICATION_METHOD = 'INCREMENTAL'

    def __init__(self, config, state, catalog, client):
        self.config = config
        self.state = state
        self.catalog = catalog
        self.client = client

    @classmethod
    def matches_catalog(cls, catalog):
        return catalog.get('stream') == cls.TABLE

    @classmethod
    def load_metadata(cls, schema):
        mdata = metadata.new()

        mdata = metadata.write(mdata, (), 'table-key-properties', cls.KEY_PROPERTIES)
        mdata = metadata.write(mdata, (), 'forced-replication-method', cls.REPLICATION_KEY)

        if cls.REPLICATION_KEY:
            mdata = metadata.write(mdata, (), 'valid-replication-keys', [cls.REPLICATION_KEY])

        for field_name in schema['properties'].keys():
            if field_name in cls.KEY_PROPERTIES or field_name == cls.REPLICATION_KEY:
                mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'automatic')
            else:
                mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'available')

        return metadata.to_list(mdata)

    def generate_catalog(self):
        cls = self.__class__

        return [{
            'tap_stream_id': cls.TABLE,
            'stream': cls.TABLE,
            'key_properties': cls.KEY_PROPERTIES,
            'schema': cls.SCHEMA,
            'metadata': cls.load_metadata(cls.SCHEMA)
        }]

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
        LOGGER.info('Syncing data for {}'.format(date.isoformat()))
        table = self.TABLE

        updated_after = date
        updated_before = updated_after + interval
        cursor = None
        has_data = True
        page = 1

        extraction_time = singer.utils.now()
        while has_data:
            url = 'https://{}.uservoice.com{}'.format(
                self.config.get('subdomain'),
                self.API_PATH)

            result = self.client.fetch_data(
                url, updated_after, updated_before, cursor,
                endpoint=table)

            cursor = result.get('pagination', {}).get('cursor')
            total_pages = result.get('pagination', {}).get('total_pages')
            data = self.get_stream_data(result)
            has_data = ((data is not None) and (len(data) > 0))

            if has_data:
                with singer.metrics.record_counter(endpoint=table) \
                     as counter:
                    for rec in data:
                        with Transformer() as transformer:
                            rec = transformer.transform(rec, self.catalog['schema'], metadata.to_map(self.catalog['metadata']))

                        singer.write_record(table, rec, time_extracted=extraction_time)
                        counter.increment()

                        rec_updated_at = rec.get(self.REPLICATION_KEY)
                        if rec_updated_at:
                            self.state = incorporate(self.state,
                                                     table,
                                                     self.REPLICATION_KEY,
                                                     rec_updated_at)

                if page == total_pages:
                    LOGGER.info('Reached end of stream, moving on.')
                    has_data = False

                elif cursor is None:
                    raise RuntimeError(('Found data, but there is no '
                                        'continuation cursor! (Expected '
                                        '{} pages, found {})').format(
                                            total_pages,
                                            page))

            else:
                LOGGER.info('No data returned, moving on.')

            page = page + 1

        self.state = incorporate(self.state,
                                 table,
                                 self.REPLICATION_KEY,
                                 date.isoformat())

        save_state(self.state)

    def sync_data(self):
        table = self.TABLE

        date = get_last_record_value_for_table(self.state, table)

        if date is None:
            date = get_config_start_date(self.config)

        interval = timedelta(days=7)

        while date < datetime.now(pytz.utc):
            self.sync_data_for_date(date, interval)

            date = date + interval

        return self.state
