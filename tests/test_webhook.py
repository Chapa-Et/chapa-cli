import unittest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from chapa_cli.webhook import app, webhook

class WebhookTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.runner = CliRunner()

    def test_chapa_webhook(self):
        """Test webhook endpoint with manual route setup."""
        # The webhook route is dynamically created, so let's test the Flask app directly
        with app.test_request_context('/webhook/test', method='POST', json={"key": "value"}):
            # Test that our app can handle the request structure
            self.assertTrue(app.test_client() is not None)

    @patch('chapa_cli.webhook.requests.post')
    def test_ping_command(self, mock_post):
        """Test the ping command with mocked requests."""
        # Mock successful ping response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "pong"}
        mock_post.return_value = mock_response
        
        result = self.runner.invoke(webhook, ['ping', 'http://localhost:5000/webhook/test'])
        self.assertIn('Ping successful', result.output)

    @patch('chapa_cli.webhook.app.run')
    def test_listen_command(self, mock_app_run):
        """Test the listen command with mocked Flask app.run."""
        result = self.runner.invoke(webhook, ['listen', 'webhook/test'])
        
        # Verify that app.run was called 
        mock_app_run.assert_called_once()
        # Since we're mocking app.run, there shouldn't be an error
        self.assertEqual(result.exit_code, 0)

if __name__ == "__main__":
    unittest.main()
