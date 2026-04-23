import unittest
from unittest.mock import patch
import requests.exceptions
from tap_uservoice.exceptions import (
    UservoiceError,
    UservoiceAuthError,
    UservoiceBadRequestError,
    UservoiceRateLimitError,
    UservoiceInternalServerError,
    UservoiceServiceUnavailableError,
)


class MockResponse:
    """Class to mock requests.Response object."""
    def __init__(self, status_code=200, json_data=None, text="", headers=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._json_data


class TestUservoiceClientInit(unittest.TestCase):
    """Test UservoiceClient initialization."""

    def test_init_sets_config(self):
        """Test that __init__ stores config."""
        from tap_uservoice.client import UservoiceClient
        config = {
            'subdomain': 'test',
            'api_key': 'key',
            'api_secret': 'secret',
        }
        client = UservoiceClient(config)
        self.assertEqual(client.config, config)


class TestAuthorize(unittest.TestCase):
    """Test the authorize method."""

    @patch('tap_uservoice.client.requests.post')
    def test_authorize_success(self, mock_post):
        """Test successful authorization sets access_token."""
        from tap_uservoice.client import UservoiceClient
        mock_post.return_value = MockResponse(
            200, {'access_token': 'new_token_123'}
        )
        config = {
            'subdomain': 'test',
            'api_key': 'key',
            'api_secret': 'secret',
        }
        client = UservoiceClient(config)
        client.authorize()
        self.assertEqual(client.access_token, 'new_token_123')
        mock_post.assert_called_once_with(
            'https://test.uservoice.com/api/v2/oauth/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': 'key',
                'client_secret': 'secret',
            },
            timeout=300
        )

    @patch('tap_uservoice.client.requests.post')
    def test_authorize_failure_raises(self, mock_post):
        """Test failed authorization raises UservoiceAuthError."""
        from tap_uservoice.client import UservoiceClient
        mock_post.return_value = MockResponse(401, text='Unauthorized')
        config = {
            'subdomain': 'test',
            'api_key': 'key',
            'api_secret': 'secret',
        }
        client = UservoiceClient(config)
        with self.assertRaises(UservoiceAuthError):
            client.authorize()


class TestFetchData(unittest.TestCase):
    """Test the fetch_data method."""

    def _make_client(self):
        """Create a UservoiceClient with mocked auth."""
        from tap_uservoice.client import UservoiceClient
        config = {
            'subdomain': 'test',
            'api_key': 'key',
            'api_secret': 'secret',
        }
        client = UservoiceClient(config)
        client.access_token = 'test_token'
        return client

    @patch('tap_uservoice.client.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test a successful API fetch returns JSON."""
        client = self._make_client()
        mock_get.return_value = MockResponse(200, {'data': 'result'})
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'result'})
        mock_get.assert_called_once()

    @patch('tap_uservoice.client.requests.get')
    def test_fetch_includes_auth_header(self, mock_get):
        """Test that fetch_data includes Authorization header."""
        client = self._make_client()
        mock_get.return_value = MockResponse(200, {'data': 'ok'})
        client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        call_kwargs = mock_get.call_args
        headers = call_kwargs[1]['headers']
        self.assertEqual(headers['Authorization'], 'Bearer test_token')

    @patch('tap_uservoice.client.requests.get')
    def test_fetch_includes_per_page(self, mock_get):
        """Test that fetch_data includes per_page=100 in params."""
        client = self._make_client()
        mock_get.return_value = MockResponse(200, {'data': 'ok'})
        client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]['params']
        self.assertEqual(params['per_page'], 100)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_429_rate_limit_retries(self, mock_get, mock_sleep):
        """Test that 429 status triggers backoff retry."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(429, headers={'Retry-After': '2'}),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)

        # Verify the retry call preserved per_page on the retry request
        second_call = mock_get.call_args_list[1]
        second_params = second_call[1]['params']
        self.assertEqual(second_params['per_page'], 100)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_429_retry_preserves_url_params_and_headers(self, mock_get, mock_sleep):
        """Test that backoff retry after 429 re-calls _make_request with
        the same URL, query params, and auth headers."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(429, headers={'Retry-After': '1'}),
            MockResponse(200, {'data': 'ok'}),
        ]
        client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        # Backoff should have retried exactly once
        self.assertEqual(mock_get.call_count, 2)

        first_call = mock_get.call_args_list[0]
        second_call = mock_get.call_args_list[1]

        # URL preserved
        self.assertEqual(first_call[0][0], second_call[0][0])
        self.assertEqual(
            first_call[0][0],
            'https://test.uservoice.com/api/v2/admin/categories')

        # Params preserved (per_page and any other params)
        self.assertEqual(first_call[1]['params'], second_call[1]['params'])
        self.assertEqual(first_call[1]['params']['per_page'], 100)

        # Auth header preserved
        self.assertEqual(
            first_call[1]['headers']['Authorization'],
            second_call[1]['headers']['Authorization'])

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_429_retry_exhausts_max_tries(self, mock_get, mock_sleep):
        """Test that repeated 429s exhaust backoff max_tries and raise."""
        client = self._make_client()
        mock_get.return_value = MockResponse(
            429, headers={'Retry-After': '0'})
        with self.assertRaises(UservoiceRateLimitError):
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories')
        self.assertEqual(mock_get.call_count, 5)

    @patch('tap_uservoice.client.requests.post')
    @patch('tap_uservoice.client.requests.get')
    def test_401_triggers_reauth(self, mock_get, mock_post):
        """Test that 401 triggers re-authorization and the retry uses the new token."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(401),
            MockResponse(200, {'data': 'ok'}),
        ]
        mock_post.return_value = MockResponse(
            200, {'access_token': 'new_token'})
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        # Re-authorization happened exactly once
        mock_post.assert_called_once()
        # Two GET calls: first got 401, second was the retry
        self.assertEqual(mock_get.call_count, 2)
        # The retry request should use the new token from re-auth
        retry_call = mock_get.call_args_list[1]
        self.assertEqual(
            retry_call[1]['headers']['Authorization'],
            'Bearer new_token')

    @patch('tap_uservoice.client.requests.get')
    def test_non_200_raises_error(self, mock_get):
        """Test that non-200 non-retryable status raises the mapped exception."""
        client = self._make_client()
        mock_get.return_value = MockResponse(400, text='Bad Request')
        with self.assertRaises(UservoiceBadRequestError):
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories')

    @patch('tap_uservoice.client.requests.get')
    def test_fetch_with_cursor(self, mock_get):
        """Test that cursor param is forwarded."""
        client = self._make_client()
        mock_get.return_value = MockResponse(200, {'data': 'ok'})
        client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            cursor='abc123',
            endpoint='categories')
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]['params']
        self.assertEqual(params['cursor'], 'abc123')

    @patch('tap_uservoice.client.requests.get')
    def test_fetch_with_updated_after(self, mock_get):
        """Test that updated_after param is forwarded."""
        from datetime import datetime
        client = self._make_client()
        mock_get.return_value = MockResponse(200, {'data': 'ok'})
        date = datetime(2024, 1, 15, 10, 30, 0)
        client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            updated_after=date,
            endpoint='categories')
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]['params']
        self.assertEqual(params['updated_after'], '2024-01-15T10:30:00.000Z')

    @patch('tap_uservoice.client.requests.get')
    def test_fetch_with_updated_before(self, mock_get):
        """Test that updated_before param is forwarded."""
        from datetime import datetime
        client = self._make_client()
        mock_get.return_value = MockResponse(200, {'data': 'ok'})
        date = datetime(2024, 6, 15, 12, 0, 0)
        client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            updated_before=date,
            endpoint='categories')
        call_kwargs = mock_get.call_args
        params = call_kwargs[1]['params']
        self.assertEqual(params['updated_before'], '2024-06-15T12:00:00.000Z')

    @patch('tap_uservoice.client.requests.get')
    def test_unknown_status_raises_base_error(self, mock_get):
        """Test that unmapped status codes raise the base UservoiceError."""
        client = self._make_client()
        mock_get.return_value = MockResponse(418, text="I'm a teapot")
        with self.assertRaises(UservoiceError):
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories')

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_connection_error_retries_and_succeeds(self, mock_get, mock_sleep):
        """Test that a transient ConnectionError is retried via backoff."""
        client = self._make_client()
        mock_get.side_effect = [
            requests.exceptions.ConnectionError('Connection refused'),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_timeout_retries_and_succeeds(self, mock_get, mock_sleep):
        """Test that a Timeout is retried via backoff."""
        client = self._make_client()
        mock_get.side_effect = [
            requests.exceptions.Timeout('Read timed out'),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_500_retries_and_succeeds(self, mock_get, mock_sleep):
        """Test that a 500 Internal Server Error is retried via backoff."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(500, text='Internal Server Error'),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_503_retries_and_succeeds(self, mock_get, mock_sleep):
        """Test that a 503 Service Unavailable is retried via backoff."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(503, text='Service Unavailable'),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_connection_error_exhausts_max_tries(self, mock_get, mock_sleep):
        """Test that persistent ConnectionError exhausts backoff and raises."""
        client = self._make_client()
        mock_get.side_effect = requests.exceptions.ConnectionError(
            'Connection refused')
        with self.assertRaises(requests.exceptions.ConnectionError):
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories')
        self.assertEqual(mock_get.call_count, 5)

    @patch('tap_uservoice.client.requests.post')
    @patch('tap_uservoice.client.requests.get')
    def test_401_reauth_failure_raises(self, mock_get, mock_post):
        """Test that if re-auth after 401 also fails, the error propagates."""
        client = self._make_client()
        mock_get.return_value = MockResponse(401)
        mock_post.return_value = MockResponse(401, text='Unauthorized')
        with self.assertRaises(UservoiceAuthError):
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories')

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_unmapped_5xx_retries_via_backoff(self, mock_get, mock_sleep):
        """Test that an unmapped 5xx (e.g. 502) is retried via backoff
        because raise_for_error maps it to UservoiceInternalServerError."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(502, text='Bad Gateway'),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_unmapped_5xx_exhausts_max_tries(self, mock_get, mock_sleep):
        """Test that persistent unmapped 5xx exhausts backoff and raises."""
        client = self._make_client()
        mock_get.return_value = MockResponse(502, text='Bad Gateway')
        with self.assertRaises(UservoiceInternalServerError):
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories')
        self.assertEqual(mock_get.call_count, 5)

    @patch('tap_uservoice.client.requests.post')
    def test_authorize_uses_timeout(self, mock_post):
        """Test that authorize() passes timeout to requests.post."""
        from tap_uservoice.client import UservoiceClient, REQUEST_TIMEOUT
        mock_post.return_value = MockResponse(
            200, {'access_token': 'token'})
        config = {
            'subdomain': 'test',
            'api_key': 'key',
            'api_secret': 'secret',
        }
        client = UservoiceClient(config)
        client.authorize()
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs[1]['timeout'], REQUEST_TIMEOUT)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_429_retry_after_header_is_parsed(self, mock_get, mock_sleep):
        """Test that Retry-After header is parsed into the exception's
        retry_after attribute and used by the backoff handler."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(429, headers={'Retry-After': '10'}),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        self.assertEqual(mock_get.call_count, 2)
        # time.sleep was called at least once (by backoff), and the
        # on_backoff handler should have overridden the wait to 10
        mock_sleep.assert_called()
        actual_wait = mock_sleep.call_args[0][0]
        self.assertEqual(actual_wait, 10)

    @patch('backoff._sync.time.sleep', return_value=None)
    @patch('tap_uservoice.client.requests.get')
    def test_429_without_retry_after_uses_expo_backoff(self, mock_get, mock_sleep):
        """Test that 429 without Retry-After header falls back to expo backoff."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(429, headers={}),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        # Still retried
        self.assertEqual(mock_get.call_count, 2)
        # Backoff used exponential wait (not overridden by handler)
        mock_sleep.assert_called()


class TestRateLimitErrorRetryAfter(unittest.TestCase):
    """Test that UservoiceRateLimitError parses Retry-After header."""

    def test_retry_after_parsed_from_header(self):
        """Test retry_after is set from Retry-After header."""
        resp = MockResponse(429, headers={'Retry-After': '30'})
        exc = UservoiceRateLimitError('rate limited', resp)
        self.assertEqual(exc.retry_after, 30)
        self.assertIn('Retry after 30 seconds', str(exc))

    def test_retry_after_zero(self):
        """Test retry_after is 0 when header is '0'."""
        resp = MockResponse(429, headers={'Retry-After': '0'})
        exc = UservoiceRateLimitError('rate limited', resp)
        self.assertEqual(exc.retry_after, 0)

    def test_retry_after_missing_header(self):
        """Test retry_after is None when header is absent."""
        resp = MockResponse(429, headers={})
        exc = UservoiceRateLimitError('rate limited', resp)
        self.assertIsNone(exc.retry_after)
        self.assertNotIn('Retry after', str(exc))

    def test_retry_after_invalid_header(self):
        """Test retry_after is None when header is non-numeric."""
        resp = MockResponse(429, headers={'Retry-After': 'abc'})
        exc = UservoiceRateLimitError('rate limited', resp)
        self.assertIsNone(exc.retry_after)

    def test_retry_after_no_response(self):
        """Test retry_after is None when no response object."""
        exc = UservoiceRateLimitError('rate limited')
        self.assertIsNone(exc.retry_after)
