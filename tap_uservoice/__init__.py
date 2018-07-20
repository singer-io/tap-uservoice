#!/usr/bin/env python3

import argparse
import json
import sys

import singer

from tap_uservoice.catalog import is_selected, load_catalog
from tap_uservoice.client import UservoiceClient
from tap_uservoice.config import load_config
from tap_uservoice.state import load_state, save_state

from tap_uservoice.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()  # noqa


def do_discover(args):
    LOGGER.info("Starting discovery.")

    config = load_config(args.config)
    state = load_state(args.state)

    catalog = []

    for available_stream in AVAILABLE_STREAMS:
        stream = available_stream(config, state, None, None)

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


def do_sync(args):
    LOGGER.info("Starting sync.")

    config = load_config(args.config)
    state = load_state(args.state)
    if args.properties:
        catalog = load_catalog(args.properties)
    elif args.catalog:
        catalog = singer.Catalog.load(args.catalog)

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
            LOGGER.error(str(e))
            LOGGER.error('Failed to sync endpoint {}, moving on!'
                         .format(stream.TABLE))

    save_state(state)


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(
        required_config_keys=['client_id', 'client_secret', 'subdomain'])

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config', help='Config file', required=True)
    parser.add_argument(
        '-s', '--state', help='State file')
    parser.add_argument(
        '-p', '--properties', help='Catalog file with fields selected')
    parser.add_argument(
        '--catalog', help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        help='Build a catalog from the underlying schema',
        action='store_true')
    parser.add_argument(
        '-S', '--select-all',
        help=('When "--discover" is set, this flag selects all fields for '
              'replication in the generated catalog'),
        action='store_true')

    args = parser.parse_args()

    if args.discover:
        do_discover(args)
    elif args.properties or args.catalog:
        do_sync(args)


if __name__ == '__main__':
    main()
