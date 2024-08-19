import unittest
from click.testing import CliRunner
from chapa_cli.webhook import app, webhook

class WebhookTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.runner = CliRunner()

    def test_chapa_webhook(self):
        response = self.app.post('/webhook/test', json={"key": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Webhook received', response.data)

    def test_ping_command(self):
        result = self.runner.invoke(webhook.commands['ping'], ['http://localhost:5000/webhook/test'])
        self.assertIn('Ping failed', result.output)


    def test_listen_command(self):
        result = self.runner.invoke(webhook.commands['listen'], ['http://localhost:5000/webhook/test'])
        self.assertIn('Running on http://0.0.0.0:5000/', result.output)

if __name__ == "__main__":
    unittest.main()
