"""
Test script for OTA updater
Run this on Raspberry Pi to test OTA logic before deploying to ESP32
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Code', 'backend'))

from ota.ota_updater import OTAUpdater

def test_version_check():
    """Test version checking"""
    print("=" * 50)
    print("TEST 1: Version Check")
    print("=" * 50)
    
    updater = OTAUpdater()
    
    print("\n1. Getting local version...")
    local_version = updater.get_local_version()
    print(f"   Local version: {local_version}")
    
    print("\n2. Getting remote version...")
    remote_data = updater.get_remote_version()
    if remote_data:
        print(f"   Remote version: {remote_data['version']}")
        print(f"   Date: {remote_data.get('date', 'N/A')}")
        print(f"   Notes: {remote_data.get('notes', 'N/A')}")
        print(f"   Files to update: {len(remote_data.get('files', []))}")
        for f in remote_data.get('files', []):
            print(f"     - {f}")
    else:
        print("   ✗ Failed to fetch remote version")
        return False
    
    return True

def test_update_check():
    """Test update availability check"""
    print("\n" + "=" * 50)
    print("TEST 2: Update Availability Check")
    print("=" * 50)
    
    updater = OTAUpdater()
    remote_data = updater.check_for_updates()
    
    if remote_data:
        print(f"\n✓ Update available to version {remote_data['version']}")
        return True
    else:
        print("\n✓ No update needed or update check failed")
        return False

def test_file_download():
    """Test downloading a single file"""
    print("\n" + "=" * 50)
    print("TEST 3: File Download Test")
    print("=" * 50)
    
    updater = OTAUpdater()
    
    # Get remote version to see what files are available
    remote_data = updater.get_remote_version()
    if not remote_data or not remote_data.get('files'):
        print("✗ No files to test download")
        return False
    
    # Try to download first file in list
    test_file = remote_data['files'][0]
    print(f"\nTesting download of: {test_file}")
    
    # Create a test download path
    test_path = f"ota_test_{test_file.replace('/', '_')}"
    
    success = updater.download_file(test_file, test_path)
    
    if success and os.path.exists(test_path):
        file_size = os.path.getsize(test_path)
        print(f"✓ Downloaded successfully: {file_size} bytes")
        
        # Clean up test file
        os.remove(test_path)
        print("✓ Cleaned up test file")
        return True
    else:
        print("✗ Download failed")
        return False

def test_full_update():
    """Test full OTA update process"""
    print("\n" + "=" * 50)
    print("TEST 4: Full OTA Update (DRY RUN)")
    print("=" * 50)
    
    print("\n⚠️  WARNING: This will perform an actual update!")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Skipped full update test")
        return False
    
    updater = OTAUpdater()
    success = updater.perform_update()
    
    if success:
        print("\n✓ Full update test passed")
    else:
        print("\n✗ Full update test failed")
    
    return success

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print(" OTA UPDATER TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Version Check", test_version_check),
        ("Update Availability", test_update_check),
        ("File Download", test_file_download),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    # Optionally run full update
    print("\n" + "=" * 60)
    response = input("\nRun full OTA update test? (yes/no): ")
    if response.lower() == 'yes':
        test_full_update()

if __name__ == "__main__":
    main()
