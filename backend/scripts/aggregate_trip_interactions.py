"""
Trip Interactions Aggregator (Phase 1)
======================================

Aggregates event data into trip_interactions table for:
- Click-through rates
- Unique viewers/clickers
- 7-day rolling metrics

Run: python scripts/aggregate_trip_interactions.py
Schedule: Hourly via cron or APScheduler
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text


def aggregate_trip_interactions():
    """
    Aggregate events into trip_interactions table.
    
    Computes:
    - Total impressions, clicks, saves, contacts
    - Unique viewers and clickers
    - Click-through rate (CTR)
    - 7-day rolling metrics
    """
    print("\n" + "="*60)
    print("AGGREGATE TRIP INTERACTIONS")
    print("="*60)
    
    with engine.connect() as conn:
        try:
            # Use event_type string values (production database has event_type as string, not event_type_id)
            impression_type = 'impression'
            click_type = 'click_trip'
            save_type = 'save_trip'
            whatsapp_type = 'contact_whatsapp'
            booking_type = 'booking_start'
            
            print(f"\nEvent types: impression='{impression_type}', click='{click_type}', save='{save_type}'")
            
            # Get all trips with events
            print("\n[STEP 1] Getting trips with events...")
            trips_with_events = conn.execute(text("""
                SELECT DISTINCT trip_id 
                FROM events 
                WHERE trip_id IS NOT NULL
            """)).fetchall()
            
            trip_ids = [row[0] for row in trips_with_events]
            print(f"  Found {len(trip_ids)} trips with events")
            
            if not trip_ids:
                print("  No trips with events found. Exiting.")
                return True
            
            # Calculate 7-day window
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            # Process each trip
            print("\n[STEP 2] Aggregating metrics per trip...")
            updated_count = 0
            
            for trip_id in trip_ids:
                # Get aggregated metrics for this trip
                # Note: Using event_type (string) instead of event_type_id (integer) for production compatibility
                metrics = conn.execute(text("""
                    SELECT 
                        -- Total counts
                        COUNT(*) FILTER (WHERE event_type = :impression_type) as impressions,
                        COUNT(*) FILTER (WHERE event_type = :click_type) as clicks,
                        COUNT(*) FILTER (WHERE event_type = :save_type) as saves,
                        COUNT(*) FILTER (WHERE event_type = :whatsapp_type) as whatsapp,
                        COUNT(*) FILTER (WHERE event_type = :booking_type) as bookings,
                        
                        -- Unique counts
                        COUNT(DISTINCT anonymous_id) FILTER (WHERE event_type = :impression_type) as unique_viewers,
                        COUNT(DISTINCT anonymous_id) FILTER (WHERE event_type = :click_type) as unique_clickers,
                        
                        -- 7-day counts
                        COUNT(*) FILTER (WHERE event_type = :impression_type AND timestamp >= :seven_days) as impressions_7d,
                        COUNT(*) FILTER (WHERE event_type = :click_type AND timestamp >= :seven_days) as clicks_7d,
                        
                        -- Last click
                        MAX(timestamp) FILTER (WHERE event_type = :click_type) as last_clicked
                    FROM events
                    WHERE trip_id = :trip_id
                """), {
                    'trip_id': trip_id,
                    'impression_type': impression_type,
                    'click_type': click_type,
                    'save_type': save_type,
                    'whatsapp_type': whatsapp_type,
                    'booking_type': booking_type,
                    'seven_days': seven_days_ago,
                }).fetchone()
                
                impressions = metrics[0] or 0
                clicks = metrics[1] or 0
                saves = metrics[2] or 0
                whatsapp = metrics[3] or 0
                bookings = metrics[4] or 0
                unique_viewers = metrics[5] or 0
                unique_clickers = metrics[6] or 0
                impressions_7d = metrics[7] or 0
                clicks_7d = metrics[8] or 0
                last_clicked = metrics[9]
                
                # Compute rates
                ctr = (clicks / impressions) if impressions > 0 else None
                save_rate = (saves / clicks) if clicks > 0 else None
                contact_rate = (whatsapp / clicks) if clicks > 0 else None
                
                # Upsert into trip_interactions
                conn.execute(text("""
                    INSERT INTO trip_interactions (
                        trip_id, impression_count, unique_viewers, click_count, unique_clickers,
                        save_count, whatsapp_contact_count, booking_start_count,
                        click_through_rate, save_rate, contact_rate,
                        impressions_7d, clicks_7d, last_clicked_at, updated_at
                    ) VALUES (
                        :trip_id, :impressions, :unique_viewers, :clicks, :unique_clickers,
                        :saves, :whatsapp, :bookings,
                        :ctr, :save_rate, :contact_rate,
                        :impressions_7d, :clicks_7d, :last_clicked, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (trip_id) DO UPDATE SET
                        impression_count = EXCLUDED.impression_count,
                        unique_viewers = EXCLUDED.unique_viewers,
                        click_count = EXCLUDED.click_count,
                        unique_clickers = EXCLUDED.unique_clickers,
                        save_count = EXCLUDED.save_count,
                        whatsapp_contact_count = EXCLUDED.whatsapp_contact_count,
                        booking_start_count = EXCLUDED.booking_start_count,
                        click_through_rate = EXCLUDED.click_through_rate,
                        save_rate = EXCLUDED.save_rate,
                        contact_rate = EXCLUDED.contact_rate,
                        impressions_7d = EXCLUDED.impressions_7d,
                        clicks_7d = EXCLUDED.clicks_7d,
                        last_clicked_at = EXCLUDED.last_clicked_at,
                        updated_at = CURRENT_TIMESTAMP
                """), {
                    'trip_id': trip_id,
                    'impressions': impressions,
                    'unique_viewers': unique_viewers,
                    'clicks': clicks,
                    'unique_clickers': unique_clickers,
                    'saves': saves,
                    'whatsapp': whatsapp,
                    'bookings': bookings,
                    'ctr': ctr,
                    'save_rate': save_rate,
                    'contact_rate': contact_rate,
                    'impressions_7d': impressions_7d,
                    'clicks_7d': clicks_7d,
                    'last_clicked': last_clicked,
                })
                
                updated_count += 1
            
            conn.commit()
            
            # Verification
            print(f"\n[VERIFICATION]")
            total_interactions = conn.execute(text(
                "SELECT COUNT(*) FROM trip_interactions"
            )).scalar()
            
            with_clicks = conn.execute(text(
                "SELECT COUNT(*) FROM trip_interactions WHERE click_count > 0"
            )).scalar()
            
            avg_ctr = conn.execute(text("""
                SELECT AVG(click_through_rate) 
                FROM trip_interactions 
                WHERE click_through_rate IS NOT NULL
            """)).scalar()
            
            print(f"  Total trip_interactions rows: {total_interactions}")
            print(f"  Trips with clicks: {with_clicks}")
            print(f"  Average CTR: {avg_ctr:.4f}" if avg_ctr else "  Average CTR: N/A")
            print(f"  Updated: {updated_count} trips")
            
            print("\n" + "="*60)
            print("AGGREGATION COMPLETE")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Aggregation failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


if __name__ == '__main__':
    success = aggregate_trip_interactions()
    exit(0 if success else 1)
