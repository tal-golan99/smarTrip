# Documentation Folder

This folder contains all project documentation, study guides, and reference materials organized by category.

## Folder Structure

**IMPORTANT:** 
- Documentation (guides, references, study materials) → `docs/` folder (this folder) - both .md and .pdf
- Practice & Learning (exercises, tests, practice code) → `learn/` folder

### Main Documentation Categories

#### 📖 Root Level Files
- **README.md** (this file) - Documentation index and overview
- **PROJECT_FILES_GUIDE.md** / **PROJECT_FILES_GUIDE.pdf** - Project structure and file organization guide
- **LEARNING_ROADMAP.pdf** - Overall learning roadmap

#### 🏗️ Architecture Documentation (`architecture/`)
Project architecture, structure, and design documentation:
- **PROJECT_STRUCTURE.md** - Overall project structure and organization
- **DESIGN_PATTERNS.md** - Design patterns used in the project
- **DESIGN_PATTERNS_README.md** - Design patterns overview
- **DATABASE_SCHEMA_FULL.md** - Complete database schema documentation
- **RESTRUCTURE_COMPLETE.md** - Restructure completion summary
- **README.md** - Architecture documentation index

#### 🔌 API Documentation (`api/`)
API endpoint documentation and reference:
- **README.md** - API endpoints reference and usage guide

#### 🔧 Technical Documentation (`technical/`)
Active technical documentation for development and troubleshooting:
- **AUTHENTICATION_FLOW.md** / **AUTHENTICATION_FLOW.pdf** - Authentication flow documentation
- **AUTHENTICATION_IMPLEMENTATION.md** - Authentication implementation details
- **BACKEND_CONNECTION_TROUBLESHOOTING.md** - Backend connection troubleshooting guide
- **ERROR_ANALYSIS_AND_SUGGESTIONS.md** - Error analysis and suggestions
- **FRONTEND_BACKEND_CONNECTION_FIX.md** - Frontend-backend connection fixes
- **INDEX_EXPLANATION.md** - Database index optimization guide
- **README_DATABASE.md** - Database documentation
- **SUPABASE_OAUTH_FIX.md** - Supabase OAuth troubleshooting
- **TROUBLESHOOTING_STEPS.md** - General troubleshooting guide
- **COLD_START_FEATURE.md** - Cold start feature documentation
- **SUGGESTIONS_CLARIFICATION.md** - Retry logic and suggestions clarification
- **CONSOLE_ERRORS_EXPLANATION.md** - Explanation of console errors
- **PRODUCTION_CONSOLE_ERRORS_EXPLANATION.md** - Production-specific error explanations
- **SESSION_START_500_ERROR_ANALYSIS.md** - Analysis of session start 500 errors
- **SESSION_START_ERROR_LOGGING_IMPLEMENTED.md** - Error logging implementation details
- **IMAGE_API_SOLUTION.md** - Solution for image API integration
- **TRIP_IMAGE_FALLBACK_SOLUTION.md** - Fallback solution for trip images

#### 🚀 Deployment & Infrastructure (`deployment/`)
Deployment guides and production configuration:
- **DEPLOYMENT.md** - General deployment guide
- **PRODUCTION_ENV_SETUP.md** - Production environment setup
- **PRODUCTION_ENV_VARIABLES.md** - Environment variables reference
- **RENDER_STEPS.md** - Render deployment steps
- **CRON_SCHEDULING_GUIDE.md** - Cron job scheduling guide

#### 📋 Feature Proposals (`proposals/`)
Feature proposals and planning documents:
- **POPULARITY_SCORE_PROPOSAL.md** - Popularity score feature proposal

#### 🧪 Testing Documentation (`testing/`)
Test plans and testing documentation:
- **MASTER_TEST_PLAN.md** - Comprehensive test plan

#### 📚 Learning Materials (`week 1/`, `week 2/`, `week 3/`, `week 4/`)
Week-by-week learning guides with deep dives:
- **week 1/** - React basics, Next.js routing, state management
- **week 2/** - HTTP APIs, TypeScript interfaces, study guides
- **week 3/** - Database models, queries, Flask basics
- **week 4/** - Event tracking, recommendation algorithm, testing & deployment

#### 🗄️ Database Migrations (`migrations/`)
Active database migration scripts:
- Migration scripts for schema changes and updates

#### 📦 Archive (`archive/`)
Historical and archived documentation:
- **archive/migration/** - Completed V1 to V2 migration documentation
- **archive/** - Completed refactoring plans, historical documentation, and archived data

#### 🛠️ Utility Scripts (`scripts/`)
Documentation utility scripts:
- **generate_learning_pdfs.py** - Generates PDFs for learning materials
- **reorganize_docs.py** - Reorganizes documentation structure

---

## Documentation Standards

When creating new documentation:
1. ✅ Create `.md` file in the appropriate subfolder
2. ✅ Generate `.pdf` version using the appropriate script if needed
3. ✅ Update this README if adding new major documentation
4. ✅ Use clear, descriptive file names

## Quick Reference

### Where to Find...

**Getting started?** → Root `README.md`  
**Frontend setup?** → `../frontend/README.md`  
**Backend setup?** → `../backend/README.md`  
**Project architecture?** → `architecture/`  
**API endpoints?** → `api/`  
**Authentication & Security?** → `technical/`  
**Database schema?** → `architecture/DATABASE_SCHEMA_FULL.md`  
**Deployment help?** → `deployment/`  
**Error troubleshooting?** → `technical/` (error docs)  
**Solutions & fixes?** → `technical/` (solution docs)  
**Feature proposals?** → `proposals/`  
**Test plans?** → `testing/`  
**Learning guides?** → `week 1/` through `week 4/`  
**Migration history?** → `archive/migration/`  
**Historical docs?** → `archive/`

### Key Documentation Files

- **[Frontend README](../frontend/README.md)** - Frontend setup, structure, and development guide
- **[Backend README](../backend/README.md)** - Backend setup, API overview, and development guide
- **[Architecture Overview](architecture/ARCHITECTURE_OVERVIEW.md)** - Complete system architecture and technology choices
- **[Design Patterns](architecture/DESIGN_PATTERNS.md)** - Design patterns used in the project
- **[Data Pipelines](architecture/DATA_PIPELINES.md)** - Detailed data flow documentation
- **[API Reference](api/README.md)** - Complete API endpoint documentation

## Practice Materials

Practice exercises and tests are located in the `learn/` folder (gitignored).
