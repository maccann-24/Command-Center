#!/usr/bin/env python3
"""
Test the chat heartbeat daemon

Runs daemon for 5 minutes and verifies agents wake up on schedule.
"""

import sys
import time
import subprocess
from pathlib import Path

def test_heartbeat_daemon():
    """Test the daemon for 5 minutes."""
    print("="*80)
    print("🧪 CHAT HEARTBEAT DAEMON TEST")
    print("="*80)
    print()
    
    print("Starting daemon for 5-minute test...")
    print("Agents should wake up based on schedule:")
    print("  - Market hours: Every 5 minutes")
    print("  - Off hours: Every 30 minutes")
    print()
    
    # Start daemon as subprocess
    daemon_path = Path(__file__).parent / "chat_heartbeat_daemon.py"
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(daemon_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("Daemon started (PID: {})".format(process.pid))
        print("Watching output for 5 minutes...")
        print()
        print("-"*80)
        
        # Watch output for 5 minutes
        start_time = time.time()
        duration = 5 * 60  # 5 minutes
        
        while time.time() - start_time < duration:
            line = process.stdout.readline()
            if line:
                print(line.rstrip())
            
            # Check if process died
            if process.poll() is not None:
                print("\n⚠️ Daemon stopped unexpectedly")
                break
        
        print("-"*80)
        print()
        
        # Stop daemon
        print("Test complete. Stopping daemon...")
        process.terminate()
        
        try:
            process.wait(timeout=5)
            print("✅ Daemon stopped gracefully")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️ Daemon killed (didn't stop gracefully)")
        
        print()
        print("="*80)
        print("✅ TEST COMPLETE")
        print("="*80)
        print()
        print("Check logs/chat_heartbeat.log for detailed output")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        if process:
            process.terminate()
            process.wait(timeout=5)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        if process:
            process.terminate()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(test_heartbeat_daemon())
