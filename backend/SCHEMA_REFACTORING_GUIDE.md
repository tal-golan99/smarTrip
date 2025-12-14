# Schema Refactoring Guide: Trip Types → Separate Table

## Overview

This refactoring separates **Trip Types** (trip styles like "Safari", "Cruise") from **Themes** (trip interests like "Wildlife", "Culture") into dedicated tables with proper relationships.

### Before (Old Schema)
```
┌─────────┐         ┌────────────┐         ┌──────┐
│  Trips  │────────▶│ trip_tags  │◀────────│ Tags │
└─────────┘         └────────────┘         └──────┘
  (Many)                                    (Many)
                                            category: 'Type' or 'Theme'
```

### After (New Schema)
```
┌─────────┐         ┌────────────┐         ┌──────┐
│  Trips  │────────▶│ trip_tags  │◀────────│ Tags │ (Themes only)
│         │         └────────────┘         └──────┘
│         │              (Many-to-Many)
│         │
│         │         ┌─────────────┐
│         │────────▶│ TripTypes   │
└─────────┘         └─────────────┘
                    (One-to-Many)
```

## Why This Refactoring?

1. **Semantic Clarity**: A trip has ONE style but MULTIPLE themes
2. **Performance**: Direct foreign key is faster than junction table for 1-to-1 relationships
3. **Data Integrity**: Enforces business rule that trip must have exactly one type
4. **Simpler Queries**: No need to filter by category when querying types

---

## Migration Steps

### Step 1: Run the Migration Script

```bash
cd backend
python migrate_types.py
```

**What it does:**
1. Creates `trip_types` table
2. Adds `trip_type_id` column to `trips` table
3. Copies all `Type` tags to `TripType` records
4. Updates all trips to reference their `TripType`
5. Deletes old `Type` tags from `tags` table
6. Cleans up `trip_tags` relationships for types

**Safety Features:**
- Idempotent (can run multiple times safely)
- Transaction-based (rolls back on error)
- 5-second countdown before execution
- Detailed logging and verification

### Step 2: Verify Migration

After running the migration, check:

```sql
-- Should return 0
SELECT COUNT(*) FROM tags WHERE category = 'Type';

-- Should match number of trip types
SELECT COUNT(*) FROM trip_types;

-- Should equal total trips (assuming all trips had a type)
SELECT COUNT(*) FROM trips WHERE trip_type_id IS NOT NULL;
```

### Step 3: Update Your Seed Script (Optional)

If you reseed the database in the future, update `seed.py` to:
1. Create `TripType` records instead of `Type` tags
2. Assign `trip_type_id` when creating trips
3. Only create `Theme` tags in the `tags` table

---

## API Changes

### New Endpoint: Get Trip Types

```http
GET /api/trip-types
```

**Response:**
```json
{
  "success": true,
  "count": 9,
  "data": [
    {
      "id": 1,
      "name": "Geographic Depth",
      "nameHe": "טיולי עומק גיאוגרפיים",
      "description": null,
      "createdAt": "2025-01-15T10:00:00",
      "updatedAt": "2025-01-15T10:00:00"
    }
  ]
}
```

### Updated Endpoint: Get Tags (Themes Only)

```http
GET /api/tags
```

Now only returns `Theme` tags. Type tags have been moved to `/api/trip-types`.

### Updated Endpoint: Get Trips

```http
GET /api/trips?include_relations=true
```

**Response includes `type` field:**
```json
{
  "id": 1,
  "title": "Safari Adventure",
  "tripTypeId": 4,
  "type": {
    "id": 4,
    "name": "African Safari",
    "nameHe": "ספארי אפריקאי"
  },
  "tags": [
    {"id": 14, "name": "Wildlife", "category": "Theme"},
    {"id": 15, "name": "Photography", "category": "Theme"}
  ]
}
```

### Updated Endpoint: Recommendations

```http
POST /api/recommendations
```

**Request Body Changes:**
```json
{
  "preferred_type_id": 4,        // NOW: Hard filter on trip_type_id
  "preferred_theme_ids": [14, 15] // STILL: Soft scoring on themes
}
```

**Behavior Changes:**
- **Trip Type**: Now a **HARD FILTER** (not scored). Only trips matching this type are returned.
- **Themes**: Still used for **SOFT SCORING**. Trips are ranked by how many themes match.

---

## Scoring Algorithm Changes

### Old Scoring (100 points total)
- Type Match: 18 pts
- Theme Match: 12 pts
- Difficulty: 13 pts
- Duration: 11 pts
- Budget: 11 pts
- Business Logic: 22 pts
- Geography: 13 pts

### New Scoring (100 points total)
- ~~Type Match: 0 pts~~ (now a hard filter)
- Theme Match: **25 pts** ↑ (increased from 12)
- Difficulty: **15 pts** ↑ (increased from 13)
- Duration: **12 pts** ↑ (increased from 11)
- Budget: **12 pts** ↑ (increased from 11)
- Business Logic: 22 pts (unchanged)
- Geography: 13 pts (unchanged)

**Rationale:** Since Type is now a hard filter, we redistributed its 18 points to other categories to maintain meaningful differentiation.

---

## Frontend Integration Changes

### 1. Fetch Trip Types Separately

**Before:**
```typescript
const tagsResponse = await fetch('/api/tags');
const typeTags = tagsResponse.data.filter(t => t.category === 'Type');
```

**After:**
```typescript
const typesResponse = await fetch('/api/trip-types');
const tripTypes = typesResponse.data; // All are types, no filtering needed
```

### 2. Update Filter UI

**Before:**
```tsx
// Type tags were checkboxes alongside theme tags
<TagSelector tags={allTags} />
```

**After:**
```tsx
// Trip types are a separate dropdown or radio buttons
<TripTypeSelect types={tripTypes} />  {/* Single selection */}
<ThemeSelector tags={themeTags} />    {/* Multiple selection */}
```

### 3. Update Recommendation Request

**Before:**
```typescript
const preferences = {
  preferred_type_id: selectedTypeTagId,  // Tag ID
  preferred_theme_ids: selectedThemeTagIds
};
```

**After:**
```typescript
const preferences = {
  preferred_type_id: selectedTripTypeId,  // TripType ID (hard filter)
  preferred_theme_ids: selectedThemeTagIds // Theme tag IDs (soft score)
};
```

---

## Database Schema Details

### TripTypes Table

```sql
CREATE TABLE trip_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    name_he VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_trip_types_name ON trip_types(name);
```

### Trips Table (Updated)

```sql
ALTER TABLE trips ADD COLUMN trip_type_id INTEGER;
ALTER TABLE trips ADD FOREIGN KEY(trip_type_id) REFERENCES trip_types(id) ON DELETE RESTRICT;
CREATE INDEX ix_trips_trip_type_id ON trips(trip_type_id);
```

### Tags Table (Unchanged Structure, Content Changed)

```sql
-- Structure remains the same
-- But now only contains records where category = 'Theme'
SELECT * FROM tags WHERE category = 'Type';  -- Returns 0 rows after migration
```

---

## Rollback Plan

If you need to rollback this migration:

1. **Stop the application**

2. **Backup your database** (CRITICAL!)
   ```bash
   pg_dump your_database > backup_before_rollback.sql
   ```

3. **Run rollback SQL:**
   ```sql
   -- Re-insert Type records into tags table
   INSERT INTO tags (name, name_he, description, category, created_at, updated_at)
   SELECT name, name_he, description, 'Type', created_at, updated_at
   FROM trip_types;
   
   -- Re-create trip_tags relationships
   INSERT INTO trip_tags (trip_id, tag_id, created_at)
   SELECT t.id, tg.id, NOW()
   FROM trips t
   JOIN trip_types tt ON t.trip_type_id = tt.id
   JOIN tags tg ON tg.name = tt.name;
   
   -- Drop the new column
   ALTER TABLE trips DROP COLUMN trip_type_id;
   
   -- Drop the new table
   DROP TABLE trip_types;
   ```

4. **Restore old code** from git
   ```bash
   git revert <commit-hash>
   ```

---

## Testing Checklist

After migration, test:

- [ ] `/api/trip-types` returns all trip types
- [ ] `/api/tags` only returns theme tags
- [ ] `/api/trips` includes `type` object in response
- [ ] `/api/recommendations` with `preferred_type_id` filters correctly
- [ ] `/api/recommendations` scoring works with themes only
- [ ] Frontend trip type dropdown displays correctly
- [ ] Frontend theme selection still works
- [ ] Search results show correct trip types and themes
- [ ] Database has 0 Type tags in tags table
- [ ] All trips have a `trip_type_id` assigned

---

## FAQs

**Q: What happens to trips without a type?**  
A: The `trip_type_id` column is nullable for migration safety. After migration, you should verify all trips have a type assigned and then make the column NOT NULL if desired.

**Q: Can I run the migration multiple times?**  
A: Yes! The migration script is idempotent. It checks if data already exists before inserting.

**Q: Will this break existing trips?**  
A: No. The migration preserves all existing data and relationships. Trips retain all their themes and gain a proper type reference.

**Q: How do I add new trip types?**  
A: Insert into `trip_types` table instead of creating Type tags:
```python
new_type = TripType(name="New Style", name_he="סגנון חדש")
db_session.add(new_type)
db_session.commit()
```

**Q: What if migration fails halfway?**  
A: The migration uses transactions and will rollback automatically on error. Check the error message and fix the issue before retrying.

---

## Support

For issues or questions about this refactoring:
1. Check the migration logs for detailed output
2. Verify database state with the SQL queries above
3. Review the CHANGES_BEFORE_AFTER.md for code examples

**Migration completed successfully?** You can now enjoy better performance and cleaner semantics!

