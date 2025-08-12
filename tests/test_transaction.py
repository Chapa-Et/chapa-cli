import unittest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from chapa_cli.transaction import transaction

class TestTransactionCommands(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('chapa_cli.transaction.load_token', return_value="test_token")
    @patch('chapa_cli.transaction.make_api_request')
    def test_banks_command(self, mock_api_request, mock_load_token):
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
                    "currency": "ETB",
                    "is_mobilemoney": False,
                    "is_rtgs": True,
                    "is_24hrs": True,
                    "is_active": True,
                    "created_at": "2023-01-01T00:00:00.000000Z",
                    "updated_at": "2023-01-01T00:00:00.000000Z"
                }
            ]
        }
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = banks_response
        mock_api_request.return_value = mock_response
        
        result = self.runner.invoke(transaction, ['banks'])
        print(f"Output: {result.output}") 
        print(f"Exception: {result.exception}")  
        self.assertIn("List of Supported Banks Information", result.output)
        self.assertIn("Test Bank", result.output)

    @patch('chapa_cli.transaction.load_token', return_value="test_token")
    @patch('chapa_cli.transaction.make_api_request')
    def test_verify_command(self, mock_api_request, mock_load_token):
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
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = verify_response
        mock_api_request.return_value = mock_response
        
        result = self.runner.invoke(transaction, ['verify', "chewatatest-6669"])
        print(f"Output: {result.output}")  
        print(f"Exception: {result.exception}") 
        self.assertIn("Payment details", result.output)

    @patch('chapa_cli.transaction.load_token', return_value="test_token")
    @patch('chapa_cli.transaction.make_api_request')
    def test_initialize_command(self, mock_api_request, mock_load_token):
        """Test the initialize transaction command."""
        init_response = {
            "message": "Transaction initialized successfully",
            "status": "success",
            "data": {
                "checkout_url": "https://checkout.chapa.co/3424234234DGSD$SDFSDF"
            }
        }
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = init_response
        mock_api_request.return_value = mock_response
        
        result = self.runner.invoke(transaction, [
            'initialize', '--amount', '100', '--phone', '0911223344'
        ])
        print(f"Output: {result.output}")  
        print(f"Exception: {result.exception}") 
        self.assertIn("Transaction initialized successfully", result.output)

if __name__ == "__main__":
    unittest.main()
