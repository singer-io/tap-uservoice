import json
import singer
from singer import metadata

LOGGER = singer.get_logger()  # noqa


def is_selected(stream):
    mdata = metadata.to_map(stream.get('metadata'))
    return mdata.get((), {}).get('selected', False)


def load_catalog(filename):
    catalog = {}

    try:
        with open(filename) as handle:
            catalog = json.load(handle)
    except Exception:
        LOGGER.fatal("Failed to decode catalog file. Is it valid json?")
        raise RuntimeError

    return catalog
