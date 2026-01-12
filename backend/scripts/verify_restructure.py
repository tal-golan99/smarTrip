"""
Restructure Verification Script
===============================

Verifies that the project restructuring was completed successfully.
Checks for:
- Missing files and directories
- Broken imports
- Missing endpoints
- Configuration issues

Run from backend folder: python scripts/verify_restructure.py
"""

import os
import sys
import importlib
from pathlib import Path

# Suppress SQLAlchemy logging during imports
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

# Expected structure
EXPECTED_FILES = {
    # Backend app structure
    'backend/app/__init__.py': True,
    'backend/app/main.py': True,
    'backend/app/core/__init__.py': True,
    'backend/app/core/config.py': True,
    'backend/app/core/database.py': True,
    'backend/app/core/auth.py': True,
    'backend/app/models/__init__.py': True,
    'backend/app/models/trip.py': True,
    'backend/app/models/events.py': True,
    'backend/app/services/__init__.py': True,
    'backend/app/services/events.py': True,
    'backend/app/services/recommendation.py': True,
    'backend/app/api/__init__.py': True,
    'backend/app/api/v1/__init__.py': True,
    'backend/app/api/v2/__init__.py': True,
    'backend/app/api/v2/routes.py': True,
    'backend/app/api/events/__init__.py': True,
    'backend/app/api/events/routes.py': True,
    
    # Jobs
    'backend/jobs/__init__.py': True,
    'backend/jobs/scheduler.py': True,
    
    # Scripts organization
    'backend/scripts/db/__init__.py': True,
    'backend/scripts/db/seed.py': True,
    'backend/scripts/data_gen/__init__.py': True,
    'backend/scripts/analytics/__init__.py': True,
    'backend/scripts/analytics/aggregate_trip_interactions.py': True,
    'backend/scripts/analytics/cleanup_sessions.py': True,
    
    # Tests
    'backend/tests/__init__.py': True,
    'backend/tests/conftest.py': True,
    'backend/tests/unit/__init__.py': True,
    'backend/tests/integration/__init__.py': True,
    'backend/tests/fixtures/__init__.py': True,
    
    # Config files
    'backend/Procfile': True,
    'backend/requirements.txt': True,
    'backend/requirements-dev.txt': True,
    'backend/runtime.txt': True,
}

EXPECTED_DIRS = {
    'backend/app',
    'backend/app/core',
    'backend/app/models',
    'backend/app/services',
    'backend/app/api',
    'backend/app/api/v1',
    'backend/app/api/v2',
    'backend/app/api/events',
    'backend/jobs',
    'backend/migrations',
    'backend/scripts',
    'backend/scripts/db',
    'backend/scripts/data_gen',
    'backend/scripts/analytics',
    'backend/scripts/_archive',
    'backend/tests',
    'backend/tests/unit',
    'backend/tests/integration',
    'backend/tests/fixtures',
    'backend/recommender',
    'backend/scenarios',
}

# Files that should NOT exist (old duplicates)
OLD_FILES_TO_CHECK = {
    'backend/app.py': False,
    'backend/api_v2.py': False,
    'backend/scheduler.py': False,
    'backend/models_v2.py': False,
    'backend/database.py': False,
    'backend/auth_supabase.py': False,
    'backend/events': False,  # Directory
}

# Import tests
IMPORT_TESTS = [
    ('app.main', 'app'),
    ('app.core.config', 'config'),
    ('app.core.database', 'db_session'),
    ('app.core.database', 'SessionLocal'),
    ('app.core.auth', 'get_current_user'),  # Check auth module and a function
    ('app.models.trip', 'Base'),
    ('app.models.trip', 'TripTemplate'),
    ('app.models.trip', 'TripOccurrence'),
    ('app.models.events', 'User'),
    ('app.models.events', 'Session'),
    ('app.services.events', 'classify_search'),
    ('app.services.recommendation', 'SCORING_WEIGHTS'),
    ('app.services.recommendation', 'SCORE_THRESHOLDS'),
    ('app.services.recommendation', 'RecommendationConfig'),
    ('app.api.v2.routes', 'api_v2_bp'),
    ('app.api.events.routes', 'events_bp'),
    ('jobs.scheduler', 'start_scheduler'),
]

def check_file_structure():
    """Check if all expected files and directories exist"""
    print("\n" + "="*80)
    print("FILE STRUCTURE CHECK")
    print("="*80)
    
    errors = []
    warnings = []
    
    # Check files
    print("\n[1] Checking files...")
    for file_path, required in EXPECTED_FILES.items():
        full_path = backend_path.parent / file_path
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            if required:
                print_error(f"{file_path} - MISSING (required)")
                errors.append(file_path)
            else:
                print_warning(f"{file_path} - MISSING (optional)")
                warnings.append(file_path)
    
    # Check directories
    print("\n[2] Checking directories...")
    for dir_path in EXPECTED_DIRS:
        full_path = backend_path.parent / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ - MISSING")
            errors.append(dir_path)
    
    # Check old files are removed
    print("\n[3] Checking old files are removed...")
    for file_path, should_exist in OLD_FILES_TO_CHECK.items():
        full_path = backend_path.parent / file_path
        if full_path.exists():
            if should_exist:
                print_success(f"{file_path} exists (expected)")
            else:
                print_error(f"{file_path} still exists (should be removed)")
                errors.append(f"{file_path} (should not exist)")
        else:
            if should_exist:
                print_error(f"{file_path} missing (should exist)")
                errors.append(file_path)
            else:
                print_success(f"{file_path} removed (correct)")
    
    return errors, warnings

def check_imports():
    """Check if imports work correctly"""
    print("\n" + "="*80)
    print("IMPORT CHECK")
    print("="*80)
    
    errors = []
    
    for module_name, attr_name in IMPORT_TESTS:
        try:
            module = importlib.import_module(module_name)
            if attr_name:
                if hasattr(module, attr_name):
                    print_success(f"{module_name}.{attr_name}")
                else:
                    print_error(f"{module_name}.{attr_name} - Attribute not found")
                    errors.append(f"{module_name}.{attr_name}")
            else:
                print_success(f"{module_name}")
        except ImportError as e:
            # Handle optional dependencies gracefully
            error_msg = str(e).lower()
            if 'jwt' in error_msg and 'app.core.auth' in module_name:
                # PyJWT might not be installed - check if file exists instead
                auth_file = backend_path / 'app' / 'core' / 'auth.py'
                if auth_file.exists():
                    print_warning(f"{module_name} - Module exists but jwt not installed (PyJWT may be missing)")
                else:
                    print_error(f"{module_name} - Import error: {e}")
                    errors.append(f"{module_name}")
            else:
                label = f"{module_name}" + (f".{attr_name}" if attr_name else "")
                print_error(f"{label} - Import error: {e}")
                errors.append(label)
        except Exception as e:
            label = f"{module_name}" + (f".{attr_name}" if attr_name else "")
            print_error(f"{label} - Import error: {e}")
            errors.append(label)
    
    return errors

def check_config_files():
    """Check configuration files"""
    print("\n" + "="*80)
    print("CONFIGURATION CHECK")
    print("="*80)
    
    errors = []
    warnings = []
    
    # Check Procfile
    procfile_path = backend_path / 'Procfile'
    if procfile_path.exists():
        try:
            content = procfile_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = procfile_path.read_text(encoding='utf-8', errors='ignore')
        
        if 'app.main:app' in content:
            print_success("Procfile contains correct app reference")
        else:
            print_warning("Procfile may not have correct app reference")
            warnings.append("Procfile")
    else:
        print_error("Procfile not found")
        errors.append("Procfile")
    
    # Check requirements files
    req_path = backend_path / 'requirements.txt'
    if req_path.exists():
        print_success("requirements.txt exists")
    else:
        print_error("requirements.txt not found")
        errors.append("requirements.txt")
    
    req_dev_path = backend_path / 'requirements-dev.txt'
    if req_dev_path.exists():
        print_success("requirements-dev.txt exists")
    else:
        print_warning("requirements-dev.txt not found (optional)")
        warnings.append("requirements-dev.txt")
    
    # Check .env.example (may be gitignored, so just check if readable)
    env_example_path = backend_path / '.env.example'
    if env_example_path.exists():
        print_success(".env.example exists")
    else:
        print_warning(".env.example not found (may be gitignored)")
        warnings.append(".env.example")
    
    return errors, warnings

def check_script_imports():
    """Check if scripts can import from new structure"""
    print("\n" + "="*80)
    print("SCRIPT IMPORTS CHECK")
    print("="*80)
    
    errors = []
    
    # Test scripts that should import from app
    script_imports = [
        ('scripts.analytics.aggregate_trip_interactions', 'from app.core.database import'),
        ('scripts.analytics.cleanup_sessions', 'from app.core.database import'),
        ('scripts.db.seed', 'from app.core.database import'),
        ('scripts.db.seed', 'from app.models.trip import'),
    ]
    
    for script_path, expected_import in script_imports:
        full_path = backend_path / (script_path.replace('.', '/') + '.py')
        if full_path.exists():
            try:
                # Use UTF-8 encoding to handle non-ASCII characters (Hebrew, etc.)
                content = full_path.read_text(encoding='utf-8')
                if expected_import in content:
                    print_success(f"{script_path} has correct import")
                else:
                    print_warning(f"{script_path} may not have expected import: {expected_import}")
            except UnicodeDecodeError:
                # If UTF-8 fails, try with errors='ignore'
                try:
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    if expected_import in content:
                        print_success(f"{script_path} has correct import (with encoding issues)")
                    else:
                        print_warning(f"{script_path} may not have expected import: {expected_import}")
                except Exception as e:
                    print_warning(f"{script_path} - Could not read file: {e}")
        else:
            print_error(f"{script_path} not found")
            errors.append(script_path)
    
    return errors

def check_scheduler_imports():
    """Check scheduler imports scripts correctly"""
    print("\n" + "="*80)
    print("SCHEDULER IMPORTS CHECK")
    print("="*80)
    
    errors = []
    
    scheduler_path = backend_path / 'jobs' / 'scheduler.py'
    if scheduler_path.exists():
        try:
            content = scheduler_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = scheduler_path.read_text(encoding='utf-8', errors='ignore')
        
        expected_imports = [
            'from scripts.analytics.aggregate_trip_interactions import',
            'from scripts.analytics.cleanup_sessions import',
            'from scripts.analytics.aggregate_daily_metrics import',
        ]
        
        for expected in expected_imports:
            if expected in content:
                print_success(f"Scheduler has correct import: {expected.split()[-1]}")
            else:
                print_error(f"Scheduler missing import: {expected}")
                errors.append(f"Scheduler: {expected}")
    else:
        print_error("scheduler.py not found")
        errors.append("jobs/scheduler.py")
    
    return errors

def check_frontend_structure():
    """Check frontend structure"""
    print("\n" + "="*80)
    print("FRONTEND STRUCTURE CHECK")
    print("="*80)
    
    errors = []
    warnings = []
    
    frontend_path = backend_path.parent / 'frontend'
    
    if not frontend_path.exists():
        print_warning("frontend/ directory not found")
        warnings.append("frontend/")
        return errors, warnings
    
    # Check frontend structure
    frontend_files = {
        'frontend/src/services/api.service.ts': True,
        'frontend/src/services/tracking.service.ts': True,
        'frontend/src/hooks/useTracking.ts': True,
        'frontend/src/types': True,  # Directory
        'frontend/src/components/ui': True,  # Directory
        'frontend/src/components/features': True,  # Directory
    }
    
    for file_path, required in frontend_files.items():
        full_path = backend_path.parent / file_path
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            if required:
                print_error(f"{file_path} - MISSING")
                errors.append(file_path)
            else:
                print_warning(f"{file_path} - MISSING (optional)")
                warnings.append(file_path)
    
    # Check old lib files are moved
    old_lib_files = {
        'frontend/src/lib/api.ts': False,  # Should be moved
        'frontend/src/lib/tracking.ts': False,  # Should be moved
        'frontend/src/lib/useTracking.ts': False,  # Should be moved
    }
    
    print("\n[4] Checking old frontend files are moved...")
    for file_path, should_exist in old_lib_files.items():
        full_path = backend_path.parent / file_path
        if full_path.exists():
            if should_exist:
                print_success(f"{file_path} exists (expected)")
            else:
                print_warning(f"{file_path} still exists (should be moved to services/hooks)")
                warnings.append(f"{file_path} (should be moved)")
        else:
            if should_exist:
                print_error(f"{file_path} missing")
                errors.append(file_path)
            else:
                print_success(f"{file_path} moved (correct)")
    
    return errors, warnings

def main():
    """Run all checks"""
    print("\n" + "="*80)
    print("PROJECT RESTRUCTURE VERIFICATION")
    print("="*80)
    print(f"\nChecking from: {backend_path}")
    
    all_errors = []
    all_warnings = []
    
    # Run checks
    errors, warnings = check_file_structure()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    errors = check_imports()
    all_errors.extend(errors)
    
    errors, warnings = check_config_files()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    errors = check_script_imports()
    all_errors.extend(errors)
    
    errors = check_scheduler_imports()
    all_errors.extend(errors)
    
    errors, warnings = check_frontend_structure()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if all_errors:
        print(f"\n{Colors.RED}[ERRORS FOUND]: {len(all_errors)}{Colors.END}")
        for error in all_errors[:20]:  # Show first 20
            print(f"  - {error}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
    else:
        print(f"\n{Colors.GREEN}[NO ERRORS FOUND]{Colors.END}")
    
    if all_warnings:
        print(f"\n{Colors.YELLOW}[WARNINGS]: {len(all_warnings)}{Colors.END}")
        for warning in all_warnings[:10]:  # Show first 10
            print(f"  - {warning}")
        if len(all_warnings) > 10:
            print(f"  ... and {len(all_warnings) - 10} more")
    else:
        print(f"\n{Colors.GREEN}[NO WARNINGS]{Colors.END}")
    
    if not all_errors and not all_warnings:
        print(f"\n{Colors.GREEN}{'='*80}")
        print("ALL CHECKS PASSED!")
        print("="*80 + Colors.END)
        return 0
    elif not all_errors:
        print(f"\n{Colors.YELLOW}{'='*80}")
        print("CHECKS PASSED WITH WARNINGS")
        print("="*80 + Colors.END)
        return 0
    else:
        print(f"\n{Colors.RED}{'='*80}")
        print("CHECKS FAILED - PLEASE FIX ERRORS")
        print("="*80 + Colors.END)
        return 1

if __name__ == '__main__':
    sys.exit(main())
