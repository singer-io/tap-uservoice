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
    except json.JSONDecodeError as e:
        LOGGER.fatal("Failed to decode catalog file. Is it valid json?")
        raise RuntimeError(
            f'Catalog file is not valid JSON: {filename}') from e
    except IOError as e:
        LOGGER.fatal("Failed to read catalog file '%s'", filename)
        raise RuntimeError(
            f'Cannot read catalog file: {filename}') from e

    return catalog
