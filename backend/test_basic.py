"""
Test basic API functionality without Prophet
"""
import sys

def test_basic_imports():
    """Test core imports"""
    print("Testing core imports...")
    try:
        from fastapi import FastAPI
        from config import settings
        from data.dimo_client import DIMOClient
        print("[OK] Core imports successful")
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def test_api_creation():
    """Test API instantiation"""
    print("Testing API creation...")
    try:
        from main import app
        print(f"[OK] API app created: {app.title}")
        return True
    except Exception as e:
        print(f"[ERROR] API creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dimo_client():
    """Test DIMO client"""
    print("Testing DIMO client...")
    try:
        from data.dimo_client import dimo_client
        # Test simulated data generation
        data = dimo_client.get_historical_data_simulation(days=7)
        if len(data) == 7:
            print(f"[OK] DIMO client working - generated {len(data)} days of data")
            return True
        else:
            print(f"[ERROR] Expected 7 days, got {len(data)}")
            return False
    except Exception as e:
        print(f"[ERROR] DIMO client failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ChainIntel Basic Functionality Test")
    print("=" * 60)
    print()

    tests = [
        test_basic_imports(),
        test_api_creation(),
        test_dimo_client(),
    ]

    print()
    print("=" * 60)
    if all(tests):
        print("[SUCCESS] All basic tests passed!")
        print("You can now start the server with: python main.py")
    else:
        print("[FAILED] Some tests failed")
    print("=" * 60)

    sys.exit(0 if all(tests) else 1)
