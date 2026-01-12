"""
Session Cleanup Job (Phase 1)
=============================

Marks stale sessions as ended and computes duration.
Sessions with no activity for 30+ minutes are considered ended.

Run: python scripts/cleanup_sessions.py
Schedule: Every 15 minutes via cron
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text


def cleanup_sessions():
    """
    Close stale sessions and compute their duration.
    
    Logic:
    1. Find sessions with ended_at IS NULL
    2. Get last event timestamp for each session
    3. If last_event > 30 minutes ago, mark as ended
    4. Compute duration_seconds
    """
    print("\n" + "="*60)
    print("SESSION CLEANUP")
    print("="*60)
    
    with engine.connect() as conn:
        try:
            # Session timeout: 30 minutes (timezone-aware)
            timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
            
            print(f"\nTimeout threshold: {timeout_threshold}")
            
            # Find active sessions
            print("\n[STEP 1] Finding active sessions...")
            active_sessions = conn.execute(text("""
                SELECT id, session_id, started_at 
                FROM sessions 
                WHERE ended_at IS NULL
            """)).fetchall()
            
            print(f"  Found {len(active_sessions)} active sessions")
            
            if not active_sessions:
                print("  No active sessions to process.")
                return True
            
            # Process each session
            print("\n[STEP 2] Processing sessions...")
            closed_count = 0
            still_active = 0
            
            for session_row in active_sessions:
                session_db_id = session_row[0]
                session_uuid = session_row[1]
                started_at = session_row[2]
                
                # Get last event for this session
                last_event = conn.execute(text("""
                    SELECT MAX(timestamp) 
                    FROM events 
                    WHERE session_id = :session_id
                """), {'session_id': str(session_uuid)}).scalar()
                
                # Make timestamps timezone-aware for comparison
                def make_aware(dt):
                    if dt is None:
                        return None
                    if dt.tzinfo is None:
                        return dt.replace(tzinfo=timezone.utc)
                    return dt
                
                started_at_aware = make_aware(started_at)
                last_event_aware = make_aware(last_event)
                
                # Determine end time
                if last_event_aware is None:
                    # No events - use started_at + 1 minute as end
                    if started_at_aware < timeout_threshold:
                        end_time = started_at + timedelta(minutes=1)
                        should_close = True
                    else:
                        should_close = False
                elif last_event_aware < timeout_threshold:
                    # Last event was before threshold - close session
                    end_time = last_event
                    should_close = True
                else:
                    # Session is still active
                    should_close = False
                
                if should_close:
                    # Compute duration
                    duration = int((end_time - started_at).total_seconds())
                    
                    # Update session
                    conn.execute(text("""
                        UPDATE sessions 
                        SET ended_at = :end_time, duration_seconds = :duration
                        WHERE id = :id
                    """), {
                        'id': session_db_id,
                        'end_time': end_time,
                        'duration': duration,
                    })
                    
                    closed_count += 1
                else:
                    still_active += 1
            
            conn.commit()
            
            # Verification
            print(f"\n[VERIFICATION]")
            total_sessions = conn.execute(text("SELECT COUNT(*) FROM sessions")).scalar()
            ended_sessions = conn.execute(text(
                "SELECT COUNT(*) FROM sessions WHERE ended_at IS NOT NULL"
            )).scalar()
            
            avg_duration = conn.execute(text("""
                SELECT AVG(duration_seconds) 
                FROM sessions 
                WHERE duration_seconds IS NOT NULL
            """)).scalar()
            
            print(f"  Total sessions: {total_sessions}")
            print(f"  Ended sessions: {ended_sessions}")
            print(f"  Still active: {still_active}")
            print(f"  Closed this run: {closed_count}")
            print(f"  Average duration: {avg_duration:.0f}s" if avg_duration else "  Average duration: N/A")
            
            print("\n" + "="*60)
            print("CLEANUP COMPLETE")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Cleanup failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


if __name__ == '__main__':
    success = cleanup_sessions()
    exit(0 if success else 1)
