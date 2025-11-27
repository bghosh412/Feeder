"""
Test script for the feeding scheduler.
This tests the scheduler_service functions without running the full system.
"""

import time
import scheduler_service
import next_feed_service
import services

def test_parse_iso_time():
    """Test ISO time parsing."""
    print("\n=== Testing ISO Time Parsing ===")
    
    iso_time = "2025-11-27T14:30:00"
    result = scheduler_service.parse_iso_time(iso_time)
    print(f"Parsing '{iso_time}':")
    print(f"  Result: {result}")
    
    invalid = "Not scheduled"
    result = scheduler_service.parse_iso_time(invalid)
    print(f"Parsing '{invalid}':")
    print(f"  Result: {result}")

def test_calculate_next_feed():
    """Test next feed calculation."""
    print("\n=== Testing Next Feed Calculation ===")
    
    # Create a test schedule
    test_schedule = {
        'feeding_times': [
            {'hour': 8, 'minute': 0, 'ampm': 'AM', 'enabled': True},
            {'hour': 8, 'minute': 0, 'ampm': 'PM', 'enabled': True}
        ],
        'days': {
            'Monday': True,
            'Tuesday': True,
            'Wednesday': True,
            'Thursday': True,
            'Friday': True,
            'Saturday': True,
            'Sunday': True
        }
    }
    
    # Save the schedule
    print("Saving test schedule...")
    services.write_schedule(test_schedule)
    
    # Calculate next feed
    print("Calculating next feed time...")
    scheduler_service.calculate_and_update_next_feed()
    
    # Read and display result
    with open(next_feed_service.NEXT_FEED_FILE, 'r') as f:
        next_feed = f.read().strip()
    print(f"Next feed time: {next_feed}")

def test_seconds_until_next_feed():
    """Test seconds calculation."""
    print("\n=== Testing Seconds Until Next Feed ===")
    
    seconds = scheduler_service.seconds_until_next_feed()
    if seconds is not None:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        print(f"Seconds until next feed: {seconds:.0f}")
        print(f"  = {hours:.1f} hours")
        print(f"  = {minutes:.1f} minutes")
    else:
        print("No scheduled feed time found")

def test_empty_schedule():
    """Test behavior with empty next_feed.txt."""
    print("\n=== Testing Empty Schedule ===")
    
    # Clear next_feed.txt
    next_feed_service.write_next_feed("")
    
    seconds = scheduler_service.seconds_until_next_feed()
    print(f"Seconds with empty schedule: {seconds}")
    print("(Should be None, which triggers immediate feed)")

if __name__ == '__main__':
    print("=" * 60)
    print("Feeding Scheduler Test Suite")
    print("=" * 60)
    
    try:
        test_parse_iso_time()
        test_calculate_next_feed()
        test_seconds_until_next_feed()
        test_empty_schedule()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import sys
        sys.print_exception(e)
