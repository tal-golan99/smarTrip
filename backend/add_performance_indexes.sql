-- Performance indexes for trip_occurrences table
-- Run this script on your database to improve query performance

-- Composite index for status + spots_left filtering (common filter combination)
CREATE INDEX IF NOT EXISTS ix_trip_occurrences_status_spots 
ON trip_occurrences(status, spots_left);

-- Composite index for start_date + status filtering (common filter combination)
CREATE INDEX IF NOT EXISTS ix_trip_occurrences_start_status 
ON trip_occurrences(start_date, status);

-- Note: These indexes will help with queries that filter by:
-- - Status (Open, Guaranteed, Last Places) AND spots_left > 0
-- - Start date >= today AND status not in ('Cancelled', 'Full')

