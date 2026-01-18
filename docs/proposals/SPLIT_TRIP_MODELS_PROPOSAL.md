# Split Trip Models Proposal

## Executive Summary

The `backend/app/models/trip.py` file currently contains **782 lines** of code, including multiple models, enums, and supporting code. This proposal outlines a structured approach to split this monolithic file into smaller, focused modules organized by domain and responsibility.

## Current State Analysis

### File Structure

**Current File**: `backend/app/models/trip.py` (782 lines)

**Contents**:
1. **Enums** (4 enums, ~40 lines)
   - `TripStatus` - Trip availability status
   - `Gender` - Guide gender
   - `Continent` - Geographic continents
   - `ReviewSource` - Review source tracking

2. **Company Model** (~50 lines)
   - `Company` - Travel company/tour operator

3. **Reference Models** (~150 lines)
   - `Country` - Destination countries
   - `Guide` - Tour guide information
   - `TripType` - Trip style categories
   - `Tag` - Theme tags

4. **Core Trip Models** (~300 lines)
   - `TripTemplate` - Trip definition ("what")
   - `TripOccurrence` - Scheduled instances ("when")

5. **Junction Tables** (~50 lines)
   - `TripTemplateTag` - Template ↔ Tag many-to-many
   - `TripTemplateCountry` - Template ↔ Country many-to-many

6. **Supporting Models** (~150 lines)
   - `PriceHistory` - Price change tracking
   - `Review` - User reviews

7. **Backward Compatibility** (~30 lines)
   - `TRIPS_COMPAT_VIEW_SQL` - SQL view definition

8. **Event Listeners** (~12 lines)
   - Price change tracking listener

### Current Import Patterns

Most imports use:
```python
from app.models.trip import TripTemplate, TripOccurrence, Country, Guide, TripType, Tag
from app.models.trip import Base  # For Base declarative base
```

### Challenges

1. **Large File Size**: 782 lines makes navigation difficult
2. **Mixed Concerns**: Enums, models, SQL views, and event listeners in one file
3. **Hard to Maintain**: Changes require scrolling through large file
4. **Poor Discoverability**: Hard to find specific models
5. **Testing Complexity**: Large file makes unit testing more complex
6. **Import Overhead**: Importing one model pulls in entire file

## Proposed Solution

### Modular Structure by Domain

Split `trip.py` into focused modules organized by domain and responsibility:

```
backend/app/models/
├── __init__.py                    # Centralized exports (backward compatible)
├── base.py                        # Base declarative base
├── enums.py                       # All enums
├── reference.py                   # Reference data models (Country, Guide, TripType, Tag)
├── company.py                     # Company model
├── template.py                    # TripTemplate model
├── occurrence.py                  # TripOccurrence model
├── junctions.py                   # Junction tables (TripTemplateTag, TripTemplateCountry)
├── reviews.py                     # Review model
├── price_history.py               # PriceHistory model
└── compat.py                      # Backward compatibility (view SQL, event listeners)
```

### Detailed File Breakdown

#### 1. `base.py` (~15 lines)

**Purpose**: Centralized declarative base for all models.

**Contents**:
```python
"""
Base declarative base for all SQLAlchemy models.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

**Why Separate**: 
- Single source of truth for Base
- Used by both `trip` and `events` models
- Can be imported without loading all models

#### 2. `enums.py` (~60 lines)

**Purpose**: All enum definitions used by trip models.

**Contents**:
- `TripStatus` enum
- `Gender` enum
- `Continent` enum
- `ReviewSource` enum

**Why Separate**:
- Enums are shared across multiple models
- Can be imported independently
- Easier to find and maintain enum values

#### 3. `reference.py` (~200 lines)

**Purpose**: Reference data models (lookup tables).

**Contents**:
- `Country` model
- `Guide` model
- `TripType` model
- `Tag` model

**Why Group Together**:
- All are reference/lookup tables
- Similar structure and purpose
- Often imported together
- No complex relationships between them

#### 4. `company.py` (~60 lines)

**Purpose**: Company model and related code.

**Contents**:
- `Company` model
- Company-specific methods

**Why Separate**:
- Distinct domain (companies vs trips)
- Can evolve independently
- Clear separation of concerns

#### 5. `template.py` (~200 lines)

**Purpose**: TripTemplate model - the core trip definition.

**Contents**:
- `TripTemplate` model
- Template-specific properties and methods
- Template relationships

**Why Separate**:
- Core model with complex logic
- Large model (~150 lines)
- Central to trip system

#### 6. `occurrence.py` (~200 lines)

**Purpose**: TripOccurrence model - scheduled trip instances.

**Contents**:
- `TripOccurrence` model
- Hybrid properties (effective_price, etc.)
- Occurrence-specific methods

**Why Separate**:
- Complex model with hybrid properties
- Large model (~150 lines)
- Distinct from template (different lifecycle)

#### 7. `junctions.py` (~70 lines)

**Purpose**: Junction tables for many-to-many relationships.

**Contents**:
- `TripTemplateTag` junction table
- `TripTemplateCountry` junction table

**Why Group Together**:
- Both are junction tables
- Similar structure
- Related functionality

#### 8. `reviews.py` (~100 lines)

**Purpose**: Review model and review-related code.

**Contents**:
- `Review` model
- Review-specific methods

**Why Separate**:
- Distinct feature (reviews vs trips)
- Can evolve independently
- May have future review-specific features

#### 9. `price_history.py` (~50 lines)

**Purpose**: PriceHistory model for tracking price changes.

**Contents**:
- `PriceHistory` model
- Price history methods

**Why Separate**:
- Distinct feature (analytics/tracking)
- May have future price analysis features
- Clear separation of concerns

#### 10. `compat.py` (~50 lines)

**Purpose**: Backward compatibility code.

**Contents**:
- `TRIPS_COMPAT_VIEW_SQL` - SQL view definition
- Event listeners (price change tracking)
- Migration helpers

**Why Separate**:
- Temporary code (for migration period)
- Can be removed later without affecting models
- Keeps main models clean

### Centralized Exports (`__init__.py`)

**Purpose**: Maintain backward compatibility by re-exporting all models.

**Contents**:
```python
"""
Trip Models Package

Centralized exports for backward compatibility.
All models can still be imported from app.models.trip
"""

# Base
from .base import Base

# Enums
from .enums import TripStatus, Gender, Continent, ReviewSource

# Reference models
from .reference import Country, Guide, TripType, Tag

# Company
from .company import Company

# Core trip models
from .template import TripTemplate
from .occurrence import TripOccurrence

# Junction tables
from .junctions import TripTemplateTag, TripTemplateCountry

# Supporting models
from .reviews import Review
from .price_history import PriceHistory

# Backward compatibility
from .compat import TRIPS_COMPAT_VIEW_SQL

# All exports for convenience
__all__ = [
    # Base
    'Base',
    # Enums
    'TripStatus', 'Gender', 'Continent', 'ReviewSource',
    # Reference
    'Country', 'Guide', 'TripType', 'Tag',
    # Company
    'Company',
    # Core
    'TripTemplate', 'TripOccurrence',
    # Junctions
    'TripTemplateTag', 'TripTemplateCountry',
    # Supporting
    'Review', 'PriceHistory',
    # Compat
    'TRIPS_COMPAT_VIEW_SQL',
]
```

**Benefits**:
- Existing imports continue to work: `from app.models.trip import TripTemplate`
- No code changes required in other files
- Can gradually migrate to direct imports
- Clear API surface

## Implementation Plan

### Phase 1: Create Base and Enums (Week 1, Day 1-2)

**Tasks**:
1. Create `base.py` with Base declarative base
2. Create `enums.py` with all enums
3. Update `trip.py` to import from new modules
4. Test imports work correctly

**Files Created**:
- `backend/app/models/base.py`
- `backend/app/models/enums.py`

**Files Modified**:
- `backend/app/models/trip.py` (imports from new modules)
- `backend/app/core/database.py` (import Base from base.py)
- `backend/app/models/events.py` (import Base from base.py)

### Phase 2: Extract Reference Models (Week 1, Day 3-4)

**Tasks**:
1. Create `reference.py` with Country, Guide, TripType, Tag
2. Update imports in `trip.py`
3. Update all files importing reference models
4. Test all imports work

**Files Created**:
- `backend/app/models/reference.py`

**Files Modified**:
- `backend/app/models/trip.py` (remove reference models, import from reference.py)
- `backend/app/api/resources/routes.py`
- `backend/app/api/v2/routes.py`
- `backend/app/services/recommendation/filters.py`
- Other files importing reference models

### Phase 3: Extract Company Model (Week 1, Day 5)

**Tasks**:
1. Create `company.py` with Company model
2. Update imports
3. Test imports

**Files Created**:
- `backend/app/models/company.py`

**Files Modified**:
- `backend/app/models/trip.py`
- Files importing Company

### Phase 4: Extract Core Trip Models (Week 2, Day 1-3)

**Tasks**:
1. Create `template.py` with TripTemplate
2. Create `occurrence.py` with TripOccurrence
3. Handle circular dependencies (templates need occurrences, occurrences need templates)
4. Update all imports
5. Test thoroughly

**Files Created**:
- `backend/app/models/template.py`
- `backend/app/models/occurrence.py`

**Files Modified**:
- `backend/app/models/trip.py`
- `backend/app/services/recommendation/scoring.py`
- `backend/app/services/recommendation/relaxed_search.py`
- `backend/app/services/recommendation/filters.py`
- `backend/app/api/v2/routes.py`
- Other files importing core models

**Circular Dependency Handling**:
```python
# template.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .occurrence import TripOccurrence

# occurrence.py
from .template import TripTemplate  # Import at runtime
```

### Phase 5: Extract Junction Tables (Week 2, Day 4)

**Tasks**:
1. Create `junctions.py` with TripTemplateTag and TripTemplateCountry
2. Update imports
3. Test relationships work correctly

**Files Created**:
- `backend/app/models/junctions.py`

**Files Modified**:
- `backend/app/models/trip.py`
- Files importing junction tables

### Phase 6: Extract Supporting Models (Week 2, Day 5)

**Tasks**:
1. Create `reviews.py` with Review model
2. Create `price_history.py` with PriceHistory model
3. Update imports
4. Test imports

**Files Created**:
- `backend/app/models/reviews.py`
- `backend/app/models/price_history.py`

**Files Modified**:
- `backend/app/models/trip.py`
- Files importing supporting models

### Phase 7: Extract Compatibility Code (Week 3, Day 1)

**Tasks**:
1. Create `compat.py` with view SQL and event listeners
2. Update imports
3. Test backward compatibility

**Files Created**:
- `backend/app/models/compat.py`

**Files Modified**:
- `backend/app/models/trip.py`
- Migration scripts using view SQL

### Phase 8: Create Centralized Exports (Week 3, Day 2)

**Tasks**:
1. Create/update `__init__.py` with all exports
2. Verify backward compatibility
3. Test all existing imports still work

**Files Modified**:
- `backend/app/models/__init__.py`

### Phase 9: Update Documentation and Cleanup (Week 3, Day 3-5)

**Tasks**:
1. Update model documentation
2. Remove old `trip.py` file (or keep as compatibility shim temporarily)
3. Update README/docs
4. Run full test suite
5. Code review

**Files Modified**:
- Documentation files
- `backend/app/models/trip.py` (remove or convert to compatibility shim)

## Migration Strategy

### Backward Compatibility Approach

**Option 1: Keep `trip.py` as Compatibility Shim** (Recommended)

Keep `trip.py` with only imports and re-exports:

```python
"""
Trip Models - Compatibility Shim

This file maintains backward compatibility.
All models are now in separate modules.
"""

# Re-export everything for backward compatibility
from .base import Base
from .enums import TripStatus, Gender, Continent, ReviewSource
from .reference import Country, Guide, TripType, Tag
from .company import Company
from .template import TripTemplate
from .occurrence import TripOccurrence
from .junctions import TripTemplateTag, TripTemplateCountry
from .reviews import Review
from .price_history import PriceHistory
from .compat import TRIPS_COMPAT_VIEW_SQL

__all__ = [
    'Base', 'TripStatus', 'Gender', 'Continent', 'ReviewSource',
    'Country', 'Guide', 'TripType', 'Tag',
    'Company',
    'TripTemplate', 'TripOccurrence',
    'TripTemplateTag', 'TripTemplateCountry',
    'Review', 'PriceHistory',
    'TRIPS_COMPAT_VIEW_SQL',
]
```

**Benefits**:
- Zero breaking changes
- Existing code continues to work
- Can migrate gradually
- Can remove shim later

**Option 2: Update All Imports** (More disruptive)

Update all imports to use new module paths:
- `from app.models.trip import TripTemplate` → `from app.models.template import TripTemplate`

**Benefits**:
- Cleaner structure
- No compatibility layer

**Drawbacks**:
- Requires updating ~20+ files
- Higher risk of breaking changes
- More testing required

**Recommendation**: Use Option 1 (compatibility shim) for initial implementation, then gradually migrate to direct imports.

## File Size Comparison

| File | Current Lines | Proposed Lines | Reduction |
|------|--------------|----------------|-----------|
| `trip.py` | 782 | ~50 (shim) or 0 (removed) | 94% |
| `base.py` | - | ~15 | New |
| `enums.py` | - | ~60 | New |
| `reference.py` | - | ~200 | New |
| `company.py` | - | ~60 | New |
| `template.py` | - | ~200 | New |
| `occurrence.py` | - | ~200 | New |
| `junctions.py` | - | ~70 | New |
| `reviews.py` | - | ~100 | New |
| `price_history.py` | - | ~50 | New |
| `compat.py` | - | ~50 | New |
| **Total** | **782** | **~1,055** | - |

**Note**: Total lines increase slightly due to:
- Import statements in each file
- File headers and docstrings
- Better organization and separation

**Benefits of Increase**:
- Each file is focused and manageable (~50-200 lines)
- Easier to navigate and understand
- Better code organization
- Easier to test individual modules

## Benefits

### 1. Maintainability

- **Focused Files**: Each file has a single, clear purpose
- **Easier Navigation**: Find models quickly by domain
- **Reduced Cognitive Load**: Smaller files are easier to understand
- **Clearer Structure**: Logical organization by domain

### 2. Testability

- **Isolated Testing**: Test each model module independently
- **Faster Tests**: Import only what's needed
- **Better Coverage**: Easier to achieve 100% coverage per module
- **Mocking**: Easier to mock dependencies

### 3. Performance

- **Faster Imports**: Import only needed models
- **Reduced Memory**: Don't load unused models
- **Better IDE Performance**: Smaller files load faster

### 4. Collaboration

- **Reduced Conflicts**: Multiple developers can work on different modules
- **Clear Ownership**: Each module has clear responsibility
- **Easier Reviews**: Smaller, focused changes

### 5. Extensibility

- **Easy to Add**: New models go in appropriate module
- **Clear Patterns**: Consistent structure across modules
- **Future-Proof**: Easy to split further if needed

## Risks and Mitigation

### Risk 1: Circular Dependencies

**Risk**: Models importing each other (e.g., TripTemplate ↔ TripOccurrence)

**Mitigation**:
- Use `TYPE_CHECKING` for type hints
- Import at runtime, not at module level for forward references
- Document dependencies clearly

### Risk 2: Breaking Changes

**Risk**: Existing imports break

**Mitigation**:
- Use compatibility shim (`trip.py` re-exports)
- Comprehensive test suite
- Gradual migration approach

### Risk 3: Import Confusion

**Risk**: Developers unsure which module to import from

**Mitigation**:
- Clear documentation
- Centralized exports in `__init__.py`
- IDE autocomplete helps

### Risk 4: Increased Complexity

**Risk**: More files to manage

**Mitigation**:
- Clear file naming conventions
- Logical organization
- Good documentation

## Testing Strategy

### Unit Tests

Test each module independently:
- `tests/unit/models/test_base.py`
- `tests/unit/models/test_enums.py`
- `tests/unit/models/test_reference.py`
- `tests/unit/models/test_template.py`
- `tests/unit/models/test_occurrence.py`
- etc.

### Integration Tests

Test model relationships:
- Template ↔ Occurrence relationships
- Junction table relationships
- Foreign key constraints

### Import Tests

Test backward compatibility:
- All existing imports still work
- New direct imports work
- No circular dependencies

## Success Metrics

### Code Quality

- [ ] Each file < 250 lines
- [ ] No circular dependencies
- [ ] All imports work correctly
- [ ] Test coverage maintained or improved

### Developer Experience

- [ ] Developers can find models quickly
- [ ] IDE autocomplete works correctly
- [ ] No confusion about where models are
- [ ] Documentation is clear

### Performance

- [ ] Import times don't increase significantly
- [ ] Memory usage doesn't increase
- [ ] Application startup time unchanged

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | 2 days | Base and enums extracted |
| Phase 2 | 2 days | Reference models extracted |
| Phase 3 | 1 day | Company model extracted |
| Phase 4 | 3 days | Core trip models extracted |
| Phase 5 | 1 day | Junction tables extracted |
| Phase 6 | 1 day | Supporting models extracted |
| Phase 7 | 1 day | Compatibility code extracted |
| Phase 8 | 1 day | Centralized exports created |
| Phase 9 | 3 days | Documentation and cleanup |
| **Total** | **15 days (3 weeks)** | **Complete refactoring** |

## Alternative Approaches

### Option 1: Split by Feature (Not Recommended)

Group by feature (e.g., `trips.py`, `reviews.py`, `pricing.py`)

**Pros**: Feature-based organization
**Cons**: Unclear boundaries, some models don't fit features

### Option 2: Single File with Sections (Current)

Keep one file with clear sections

**Pros**: Simple, everything in one place
**Cons**: Still 782 lines, hard to navigate

### Option 3: Domain-Driven Split (Recommended)

Split by domain/responsibility (this proposal)

**Pros**: Clear organization, logical grouping
**Cons**: Slightly more files to manage

## Conclusion

Splitting `trip.py` into focused modules will significantly improve maintainability, testability, and developer experience. The proposed structure organizes models by domain while maintaining backward compatibility through a compatibility shim. The 3-week implementation plan provides a structured, low-risk approach to refactoring.

## Next Steps

1. **Review and Approve**: Get stakeholder approval
2. **Set Up Branch**: Create feature branch for refactoring
3. **Start Phase 1**: Begin with base and enums (lowest risk)
4. **Iterate**: Complete phases incrementally
5. **Test Thoroughly**: Run full test suite after each phase
6. **Document**: Update documentation as you go
7. **Review**: Code review after each phase

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Proposal - Pending Approval
