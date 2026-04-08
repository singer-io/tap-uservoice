import unittest
from unittest.mock import patch, MagicMock


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
            }
        )

    @patch('tap_uservoice.client.requests.post')
    def test_authorize_failure_raises(self, mock_post):
        """Test failed authorization raises RuntimeError."""
        from tap_uservoice.client import UservoiceClient
        mock_post.return_value = MockResponse(401, text='Unauthorized')
        config = {
            'subdomain': 'test',
            'api_key': 'key',
            'api_secret': 'secret',
        }
        client = UservoiceClient(config)
        with self.assertRaises(RuntimeError):
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

    @patch('tap_uservoice.client.time.sleep')
    @patch('tap_uservoice.client.requests.get')
    def test_429_rate_limit_retries(self, mock_get, mock_sleep):
        """Test that 429 status triggers retry with sleep and preserves
        the endpoint argument on the recursive call."""
        client = self._make_client()
        mock_get.side_effect = [
            MockResponse(429, headers={'Retry-After': '2'}),
            MockResponse(200, {'data': 'ok'}),
        ]
        result = client.fetch_data(
            'https://test.uservoice.com/api/v2/admin/categories',
            endpoint='categories')
        self.assertEqual(result, {'data': 'ok'})
        mock_sleep.assert_called_once_with(2)
        self.assertEqual(mock_get.call_count, 2)

        # Verify the retry call incremented tries and preserved endpoint
        second_call = mock_get.call_args_list[1]
        second_params = second_call[1]['params']
        # per_page should still be present on the retry request
        self.assertEqual(second_params['per_page'], 100)

    @patch('tap_uservoice.client.requests.post')
    @patch('tap_uservoice.client.requests.get')
    def test_401_triggers_reauth(self, mock_get, mock_post):
        """Test that 401 status triggers re-authorization."""
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
        mock_post.assert_called_once()

    @patch('tap_uservoice.client.requests.get')
    def test_non_200_raises_runtime_error(self, mock_get):
        """Test that non-200 non-retryable status raises RuntimeError."""
        client = self._make_client()
        mock_get.return_value = MockResponse(400, text='Bad Request')
        with self.assertRaises(RuntimeError):
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
    def test_max_tries_exceeded_raises(self, mock_get):
        """Test that exceeding MAX_TRIES raises RuntimeError."""
        client = self._make_client()
        with self.assertRaises(RuntimeError) as ctx:
            client.fetch_data(
                'https://test.uservoice.com/api/v2/admin/categories',
                endpoint='categories',
                tries=6)
        self.assertIn('too many times', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
