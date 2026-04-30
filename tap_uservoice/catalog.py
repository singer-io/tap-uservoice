import singer
from singer import metadata

LOGGER = singer.get_logger()  # noqa


def is_selected(stream):
    mdata = metadata.to_map(stream.get('metadata'))
    return mdata.get((), {}).get('selected', False)
