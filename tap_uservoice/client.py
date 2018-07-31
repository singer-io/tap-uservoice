import time
import requests
import singer
import singer.metrics

LOGGER = singer.get_logger()  # noqa


class UservoiceClient:

    MAX_TRIES = 5

    def __init__(self, config):
        self.config = config

    def authorize(self):
        LOGGER.info('Authorizing with Uservoice API')

        url = ('https://{}.uservoice.com/api/v2/oauth/token'
               .format(self.config.get('subdomain')))

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
        }

        response = requests.post(url, data=data)

        if response.status_code != 200:
            LOGGER.error(response.text)
            raise RuntimeError('Failed to authorize with Uservoice API!')

        self.access_token = response.json().get('access_token')

    def fetch_data(self,
                   url,
                   updated_after=None,
                   updated_before=None,
                   cursor=None,
                   endpoint=None,
                   tries=0):

        if tries > self.MAX_TRIES:
            raise RuntimeError('Tried request too many times, exiting.')

        request_data = {}

        if updated_before:
            request_data['updated_before'] = \
                updated_before.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if updated_after:
            request_data['updated_after'] = \
                updated_after.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if cursor:
            request_data['cursor'] = cursor

        request_data['per_page'] = 100

        with singer.metrics.http_request_timer(endpoint):
            response = requests.get(
                url,
                headers={
                    'Authorization': 'Bearer {}'.format(
                        self.access_token)
                },
                params=request_data)

        if response.status_code == 401:
            self.authorize()
            return self.fetch_data(
                url, updated_after, updated_before, cursor, endpoint,
                tries+1)

        elif response.status_code == 429:
            sleep_time = 5
            sleep_time_str = response.headers.get('Retry-After', None)
            if sleep_time_str:
                sleep_time = int(sleep_time_str)
            LOGGER.warning('Got a 429, sleeping {} seconds '
                           'and then trying again.'.format(str(sleep_time)))
            time.sleep(sleep_time)
            return self.fetch_data(
                url, updated_after, updated_before, cursor, tries+1)

        elif response.status_code != 200:
            LOGGER.error(response.text)
            raise RuntimeError('Stream returned code {}, exiting!'
                               .format(response.status_code))

        return response.json()
