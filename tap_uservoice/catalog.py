import json
import singer
from singer import metadata

LOGGER = singer.get_logger()  # noqa


def is_selected(stream):
    # try metadata first
    mdata = metadata.to_map(stream.get('metadata'))
    if mdata.get((), {}).get('selected', False):
        return True

    # fallback to legacy way
    schema = stream.get('schema')
    default = schema.get('selected-by-default', False)
    return ((schema.get('inclusion') == 'automatic') or
            (schema.get('inclusion') == 'available' and
             schema.get('selected', default) is True))

def load_catalog(filename):
    catalog = {}

    try:
        with open(filename) as handle:
            catalog = json.load(handle)
    except Exception:
        LOGGER.fatal("Failed to decode catalog file. Is it valid json?")
        raise RuntimeError

    return catalog
