"""
Integration tests using real Chapa Test API.
These tests make actual API calls to verify full functionality.

NOTE: These tests require:
1. Internet connection
2. Valid test API keys in .env file  
3. Chapa test environment to be operational

Run with: pytest tests/test_integration.py -v -s
"""

import unittest
import os
from click.testing import CliRunner
from chapa_cli.transaction import transaction
from chapa_cli.utils import load_token
import time


class RealAPIIntegrationTests(unittest.TestCase):
    """Integration tests using real Chapa API calls."""
    
    def setUp(self):
        self.runner = CliRunner()
        self.token = load_token()
        
        # Skip if no token available
        if not self.token:
            self.skipTest("No API token found. Please set CHAPA_SECRET_KEY in .env file")
        
        if not self.token.startswith("CHASECK_TEST"):
            self.skipTest("Integration tests require TEST API keys only")
    
    def test_real_banks_api_call(self):
        """Test real API call to get supported banks."""
        print(f"\n🌐 Making REAL API call to Chapa Banks endpoint...")
        print(f"📍 Using test API token...")
        
        result = self.runner.invoke(transaction, ['banks'])
        
        print(f"✅ Result exit code: {result.exit_code}")
        
        # Should succeed
        self.assertEqual(result.exit_code, 0)
        
        # Should contain table with bank information
        self.assertIn("List of Supported Banks Information", result.output)
        
        # Should contain actual bank data
        # Ethiopian banks that Chapa supports
        self.assertTrue(
            any(bank in result.output.lower() for bank in [
                'bank', 'commercial', 'birr', 'ethiopia', 'cbe'
            ]),
            "Should contain real bank names"
        )
        
        print("✅ Real banks API call SUCCESSFUL!")
    
    def test_real_transaction_initialization(self):
        """Test real API call to initialize transaction."""
        print(f"\n🌐 Making REAL API call to initialize transaction...")
        
        # Use valid test data
        result = self.runner.invoke(transaction, [
            'initialize',
            '--amount', '50',  # Small amount for testing
            '--email', 'dummy@gmail.com',  # Test email
            '--phone', '+251911123456',  # Test Ethiopian phone
            '--currency', 'ETB',
            '--account-type', 'individual'
        ])
        
        print(f"✅ Result exit code: {result.exit_code}")
        print(f"📄 Output: {result.output}")
        
        # Should succeed  
        self.assertEqual(result.exit_code, 0)
        
        # Should contain success indicators
        self.assertIn("Transaction initialized successfully", result.output)
        self.assertIn("Checkout URL", result.output)
        self.assertIn("https://checkout.chapa.co", result.output)
        
        print("✅ Real transaction initialization SUCCESSFUL!")
    
    def test_real_transaction_validation_limits(self):
        """Test that our validation works with real API."""
        print(f"\n🛡️ Testing validation against real API limits...")
        
        # Test amount that exceeds individual limits
        result = self.runner.invoke(transaction, [
            'initialize', 
            '--amount', '75000',  # Exceeds 50K individual limit
            '--email', 'dummy@gmail.com',
            '--account-type', 'individual'
        ])
        
        print(f"📄 Validation output: {result.output}")
        
        # Should fail validation BEFORE hitting API
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("exceeds maximum transaction limit", result.output)
        self.assertIn("50000", result.output)  
        self.assertIn("individual_unapproved", result.output)
        
        print("✅ Validation correctly prevents invalid API calls!")
    
    def test_real_email_validation(self):
        """Test email validation with real scenarios."""
        print(f"\n📧 Testing email validation...")
        
        # Test invalid email
        result = self.runner.invoke(transaction, [
            'initialize',
            '--amount', '100',
            '--email', 'invalid-email-format',
            '--account-type', 'individual'
        ])
        
        print(f"📄 Email validation output: {result.output}")
        
        # Should fail validation
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Invalid email address", result.output)
        
        print("✅ Email validation working correctly!")

    def test_real_phone_validation(self):
        """Test phone validation with real scenarios.""" 
        print(f"\n📱 Testing phone validation...")
        
        # Test invalid phone
        result = self.runner.invoke(transaction, [
            'initialize',
            '--amount', '100', 
            '--email', 'dummy@gmail.com',
            '--phone', '123',  # Test with short phone num
            '--account-type', 'individual'
        ])
        
        print(f"📄 Phone validation output: {result.output}")
        
        # Should fail validation
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Invalid phone number", result.output)
        
        print("✅ Phone validation working correctly!")

if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
