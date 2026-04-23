import time
import backoff
import requests
import requests.exceptions
import singer
import singer.metrics

from tap_uservoice.exceptions import (
    ERROR_CODE_EXCEPTION_MAPPING,
    UservoiceError,
    UservoiceBackoffError,
    UservoiceAuthError,
    UservoiceUnauthorizedError,
    UservoiceRateLimitError,
    UservoiceInternalServerError,
    UservoiceServiceUnavailableError,
)

LOGGER = singer.get_logger()  # noqa
REQUEST_TIMEOUT = 300


def wait_if_retry_after(details):
    """Backoff handler that checks for a 'retry_after' attribute in the exception
    and sleeps for the specified duration to respect API rate limits.
    """
    exc = details.get('exception')
    if exc is None:
        args = details.get('args') or ()
        exc = args[0] if args else None
    if exc and hasattr(exc, 'retry_after') and exc.retry_after is not None:
        LOGGER.info('Rate limited. Honoring Retry-After: %s seconds', exc.retry_after)
        time.sleep(exc.retry_after)


def raise_for_error(response: requests.Response) -> None:
    """Raises the associated response exception. Takes in a response object,
    checks the status code, and throws the associated exception based on the
    status code.

    :param response: requests.Response object
    """
    try:
        response_json = response.json()
    except Exception:
        response_json = {}
    if response.status_code not in [200, 201, 204]:
        if response_json.get("error"):
            message = f"HTTP-error-code: {response.status_code}, Error: {response_json.get('error')}"
        else:
            error_message = ERROR_CODE_EXCEPTION_MAPPING.get(
                response.status_code, {}
            ).get("message", "Unknown Error")
            message = f"HTTP-error-code: {response.status_code}, Error: {response_json.get('message', error_message)}"

        exc = ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get(
            "raise_exception", UservoiceError
        )

        # For unmapped 5xx errors, raise a retryable server-error exception
        # so that _make_request's @backoff.on_exception actually retries them.
        if 500 <= response.status_code < 600 and response.status_code not in ERROR_CODE_EXCEPTION_MAPPING:
            exc = UservoiceInternalServerError

        raise exc(message, response) from None


class UservoiceClient:

    def __init__(self, config):
        self.config = config

    def authorize(self):
        LOGGER.info('Authorizing with Uservoice API')

        url = ('https://{}.uservoice.com/api/v2/oauth/token'
               .format(self.config.get('subdomain')))

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.get('api_key'),
            'client_secret': self.config.get('api_secret'),
        }

        try:
            response = requests.post(url, data=data, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise UservoiceAuthError(
                f'Network error during authorization: {e}') from e

        if response.status_code != 200:
            LOGGER.error(response.text)
            raise UservoiceAuthError(
                f'Failed to authorize with Uservoice API '
                f'(status {response.status_code})')

        self.access_token = response.json().get('access_token')

    def fetch_data(self,
                   url,
                   updated_after=None,
                   updated_before=None,
                   cursor=None,
                   endpoint=None):

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
            response = self._make_request(url, request_data, endpoint)

        if response.status_code == 204:
            return {}

        try:
            return response.json()
        except ValueError as e:
            raise UservoiceError(
                f'Invalid JSON in response for {endpoint}') from e

    @backoff.on_exception(
        wait_gen=lambda: backoff.expo(factor=2),
        on_backoff=wait_if_retry_after,
        exception=(
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            UservoiceRateLimitError,
            UservoiceInternalServerError,
            UservoiceServiceUnavailableError,
        ),
        max_tries=5,
        jitter=None,
    )
    def _make_request(self, url, params, endpoint):
        """Perform the HTTP GET with retry via backoff decorator."""
        try:
            response = requests.get(
                url,
                headers={
                    'Authorization': 'Bearer {}'.format(
                        self.access_token)
                },
                params=params,
                timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            LOGGER.error('Network error fetching %s: %s', endpoint, e)
            raise

        if response.status_code == 401:
            LOGGER.info('Got 401, re-authorizing and retrying.')
            self.authorize()
            response = requests.get(
                url,
                headers={
                    'Authorization': 'Bearer {}'.format(
                        self.access_token)
                },
                params=params,
                timeout=REQUEST_TIMEOUT)

        raise_for_error(response)
        return response
