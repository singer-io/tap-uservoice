#!/usr/bin/env python3

import json
import sys

import singer

from tap_uservoice.catalog import is_selected
from tap_uservoice.client import UservoiceClient
from tap_uservoice.state import save_state

from tap_uservoice.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()  # noqa

REQUIRED_CONFIG_KEYS = ['api_key', 'api_secret', 'subdomain']


def do_discover(config):
    LOGGER.info("Starting discovery.")

    catalog = []

    for available_stream in AVAILABLE_STREAMS:
        stream = available_stream(config, {}, None, None)

        catalog += stream.generate_catalog()

    json.dump({'streams': catalog}, sys.stdout, indent=4)


def get_streams_to_replicate(config, state, catalog, client):
    streams = []

    for stream_catalog in catalog.get('streams'):
        if not is_selected(stream_catalog):
            LOGGER.info("'{}' is not marked selected, skipping."
                        .format(stream_catalog.get('stream')))
            continue

        for available_stream in AVAILABLE_STREAMS:
            if available_stream.matches_catalog(stream_catalog):
                streams.append(available_stream(
                    config, state, stream_catalog, client))

                break

    return streams


def do_sync(config, state, catalog):
    LOGGER.info("Starting sync.")

    client = UservoiceClient(config)
    client.authorize()

    streams = get_streams_to_replicate(config, state, catalog, client)

    for stream in streams:
        try:
            stream.state = state
            stream.sync()
            state = stream.state
        except OSError as e:
            LOGGER.error(str(e))
            exit(e.errno)

        except Exception as e:
            LOGGER.error('Failed to sync endpoint %s: %s',
                         stream.TABLE, e, exc_info=True)
            raise

    save_state(state)


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.discover:
        do_discover(args.config)
    elif args.catalog:
        do_sync(args.config, args.state, args.catalog.to_dict())
    elif args.properties:
        do_sync(args.config, args.state, args.properties)


if __name__ == '__main__':
    main()
