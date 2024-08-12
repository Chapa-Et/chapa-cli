import unittest
from chapa_cli.transaction import get_transactions

class TestTransactionCommands(unittest.TestCase):

    def test_get_transactions(self):

        token = "test_token"
        result = get_transactions(token)
        
        self.assertIsNotNone(result)  

if __name__ == "__main__":
    unittest.main()
