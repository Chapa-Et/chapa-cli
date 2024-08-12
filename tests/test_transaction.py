import unittest
from click.testing import CliRunner
from unittest.mock import patch
import requests_mock
from chapa_cli.transaction import transaction

class TestTransactionCommands(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('chapa_cli.transaction.load_token', return_value="test_token")
    @requests_mock.Mocker()
    def test_banks_command(self, mock, load_token_mock):
        """Test the banks command."""
        banks_response = {
            "message": "Banks retrieved",
            "data": [
                {
                    "id": 1,
                    "slug": "test_bank",
                    "swift": "TSTBKTAA",
                    "name": "Test Bank",
                    "acct_length": 16,
                    "currency": "ETB"
                }
            ]
        }
        mock.get("https://api.chapa.co/v1/banks", json=banks_response, status_code=200)
        
        result = self.runner.invoke(transaction.commands['banks'])
        print(f"Output: {result.output}") 
        print(f"Exception: {result.exception}")  
        self.assertIn("Banks retrieved", result.output)

    @patch('chapa_cli.transaction.load_token', return_value="test_token")
    @requests_mock.Mocker()
    def test_verify_command(self, mock, load_token_mock):
        """Test the verify transaction command."""
        verify_response = {
            "message": "Payment details",
            "status": "success",
            "data": {
                "first_name": "Bilen",
                "last_name": "Gizachew",
                "email": "abebech_bekele@gmail.com",
                "currency": "ETB",
                "amount": 100,
                "charge": 3.5,
                "mode": "test",
                "method": "test",
                "type": "API",
                "status": "success",
                "reference": "6jnheVKQEmy",
                "tx_ref": "chewatatest-6669",
                "created_at": "2023-02-02T07:05:23.000000Z",
                "updated_at": "2023-02-02T07:05:23.000000Z"
            }
        }
        mock.get("https://api.chapa.co/v1/transaction/verify/chewatatest-6669", json=verify_response, status_code=200)
        
        result = self.runner.invoke(transaction.commands['verify'], ["chewatatest-6669"])
        print(f"Output: {result.output}")  
        print(f"Exception: {result.exception}") 
        self.assertIn("Payment details", result.output)

    @patch('chapa_cli.transaction.load_token', return_value="test_token")
    @requests_mock.Mocker()
    def test_initialize_command(self, mock, load_token_mock):
        """Test the initialize transaction command."""
        init_response = {
            "message": "Transaction initialized successfully",
            "status": "success",
            "data": {
                "checkout_url": "https://checkout.chapa.co/3424234234DGSD$SDFSDF#"
            }
        }
        mock.post("https://api.chapa.co/v1/transaction/initialize", json=init_response, status_code=200)
        
        result = self.runner.invoke(transaction.commands['initialize'], [
            '--amount', '100', '--phone', '0911223344'
        ])
        print(f"Output: {result.output}")  
        print(f"Exception: {result.exception}") 
        self.assertIn("Transaction initialized successfully", result.output)

if __name__ == "__main__":
    unittest.main()
