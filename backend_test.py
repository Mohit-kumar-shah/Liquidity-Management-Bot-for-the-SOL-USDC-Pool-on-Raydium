
import requests
import sys
import time
from datetime import datetime

class SolanaLiquidityBotTester:
    def __init__(self, base_url="https://3f51fec3-87d2-4136-9163-ca951fef9bd4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")

            return success, response.json() if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_health(self):
        """Test API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "/api/",
            200
        )

    def test_bot_status(self):
        """Test bot status endpoint"""
        return self.run_test(
            "Bot Status",
            "GET",
            "/api/status",
            200
        )

    def test_current_price(self):
        """Test current price endpoint"""
        return self.run_test(
            "Current SOL Price",
            "GET",
            "/api/price",
            200
        )

    def test_wallet_info(self):
        """Test wallet info endpoint"""
        return self.run_test(
            "Wallet Information",
            "GET",
            "/api/wallet",
            200
        )

    def test_positions(self):
        """Test positions endpoint"""
        return self.run_test(
            "Liquidity Positions",
            "GET",
            "/api/positions",
            200
        )

    def test_logs(self):
        """Test logs endpoint"""
        return self.run_test(
            "Bot Activity Logs",
            "GET",
            "/api/logs",
            200
        )

    def test_start_bot(self):
        """Test start bot endpoint (should fail without wallet configured)"""
        return self.run_test(
            "Start Bot (Expected to fail without wallet)",
            "POST",
            "/api/start",
            400
        )

    def test_stop_bot(self):
        """Test stop bot endpoint"""
        return self.run_test(
            "Stop Bot",
            "POST",
            "/api/stop",
            200
        )

    def test_discord_notification(self):
        """Test Discord notification endpoint"""
        return self.run_test(
            "Test Discord Notification",
            "POST",
            "/api/test-notification",
            200
        )

def main():
    # Setup
    tester = SolanaLiquidityBotTester()
    
    # Run tests
    tester.test_api_health()
    tester.test_bot_status()
    tester.test_current_price()
    tester.test_wallet_info()
    tester.test_positions()
    tester.test_logs()
    tester.test_start_bot()
    tester.test_stop_bot()
    tester.test_discord_notification()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
