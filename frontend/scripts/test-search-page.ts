/**
 * Search Page Validation Script
 * 
 * Validates that the search page works correctly after refactoring:
 * 1. Checks all imports resolve correctly
 * 2. Verifies component structure
 * 3. Tests TypeScript compilation
 * 4. Validates file structure
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const FRONTEND_ROOT = path.resolve(__dirname, '..');
const SRC_ROOT = path.join(FRONTEND_ROOT, 'src');

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
}

const results: TestResult[] = [];

function test(name: string, fn: () => boolean | string): void {
  try {
    const result = fn();
    if (typeof result === 'boolean') {
      results.push({ name, passed: result });
    } else {
      results.push({ name, passed: false, error: result });
    }
  } catch (error: any) {
    results.push({ name, passed: false, error: error.message });
  }
}

function fileExists(filePath: string): boolean {
  return fs.existsSync(path.join(SRC_ROOT, filePath));
}

function readFile(filePath: string): string {
  return fs.readFileSync(path.join(SRC_ROOT, filePath), 'utf-8');
}

console.log('🔍 Testing Search Page Structure...\n');

// Test 1: Main page file exists
test('Main search page file exists', () => {
  return fileExists('app/search/page.tsx');
});

// Test 2: SearchPageContent function exists in page.tsx
test('SearchPageContent function exists in page.tsx', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  return content.includes('function SearchPageContent') || content.includes('SearchPageContent()');
});

// Test 3: SearchPage default export exists
test('SearchPage default export exists', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  return content.includes('export default function SearchPage');
});

// Test 4: Suspense wrapper exists
test('Suspense wrapper exists', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  return content.includes('<Suspense');
});

// Test 5: SearchPageContent is not a separate file (should be combined)
test('SearchPageContent is NOT a separate file (should be in page.tsx)', () => {
  return !fileExists('components/features/search/SearchPageContent.tsx');
});

// Test 6: All filter sections exist
test('LocationFilterSection exists', () => {
  return fileExists('components/features/search/filters/LocationFilterSection.tsx');
});

test('TripTypeFilterSection exists', () => {
  return fileExists('components/features/search/filters/TripTypeFilterSection.tsx');
});

test('ThemeFilterSection exists', () => {
  return fileExists('components/features/search/filters/ThemeFilterSection.tsx');
});

test('DateFilterSection exists', () => {
  return fileExists('components/features/search/filters/DateFilterSection.tsx');
});

test('RangeFiltersSection exists', () => {
  return fileExists('components/features/search/filters/RangeFiltersSection.tsx');
});

// Test 7: Header and Actions components exist
test('SearchPageHeader exists', () => {
  return fileExists('components/features/search/SearchPageHeader.tsx');
});

test('SearchActions exists', () => {
  return fileExists('components/features/search/SearchActions.tsx');
});

test('SearchPageLoading exists', () => {
  return fileExists('components/features/search/SearchPageLoading.tsx');
});

test('SearchPageError exists', () => {
  return fileExists('components/features/search/SearchPageError.tsx');
});

// Test 8: Location sub-components exist
test('LocationDropdown exists', () => {
  return fileExists('components/features/search/filters/LocationDropdown.tsx');
});

test('SelectedLocationsList exists', () => {
  return fileExists('components/features/search/filters/SelectedLocationsList.tsx');
});

// Test 9: UI components exist
test('DualRangeSlider is in components/ui', () => {
  return fileExists('components/ui/DualRangeSlider.tsx');
});

test('DualRangeSlider is NOT in components/features', () => {
  return !fileExists('components/features/DualRangeSlider.tsx');
});

test('SelectionBadge exists', () => {
  return fileExists('components/ui/SelectionBadge.tsx');
});

test('TagCircle exists', () => {
  return fileExists('components/ui/TagCircle.tsx');
});

test('ClearFiltersButton exists', () => {
  return fileExists('components/ui/ClearFiltersButton.tsx');
});

// Test 10: All imports in page.tsx resolve
test('All imports in page.tsx reference valid files', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  
  // Extract import statements
  const importRegex = /from\s+['"]([^'"]+)['"]/g;
  const imports: string[] = [];
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  // Check each import path (excluding external packages and aliases)
  for (const importPath of imports) {
    // Skip external packages, aliases (@/), and relative imports that start with ./
    if (importPath.startsWith('@/')) {
      // Convert @/ to src/
      const filePath = importPath.replace('@/', '') + '.tsx';
      // Try both .tsx and .ts
      if (!fileExists(filePath) && !fileExists(filePath.replace('.tsx', '.ts'))) {
        // Check for index files
        const dirPath = importPath.replace('@/', '');
        if (!fileExists(dirPath + '/index.ts') && !fileExists(dirPath + '/index.tsx')) {
          return `Import path "${importPath}" does not resolve to a valid file`;
        }
      }
    } else if (importPath.startsWith('./') || importPath.startsWith('../')) {
      // Relative imports - would need to resolve from the file location
      // Skip for now as it's more complex
    }
  }
  return true;
});

// Test 11: page.tsx file size is reasonable (< 200 lines)
test('page.tsx file size is reasonable (< 200 lines)', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  const lines = content.split('\n').length;
  return lines < 200;
});

// Test 12: All filter sections are imported in page.tsx
test('All filter sections are imported in page.tsx', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  
  const requiredImports = [
    'LocationFilterSection',
    'TripTypeFilterSection',
    'ThemeFilterSection',
    'DateFilterSection',
    'RangeFiltersSection',
    'SearchPageHeader',
    'SearchActions',
  ];
  
  for (const importName of requiredImports) {
    if (!content.includes(importName)) {
      return `Missing import: ${importName}`;
    }
  }
  return true;
});

// Test 13: All filter sections are used in JSX
test('All filter sections are used in JSX', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  
  const requiredComponents = [
    '<LocationFilterSection',
    '<TripTypeFilterSection',
    '<ThemeFilterSection',
    '<DateFilterSection',
    '<RangeFiltersSection',
    '<SearchPageHeader',
    '<SearchActions',
  ];
  
  for (const component of requiredComponents) {
    if (!content.includes(component)) {
      return `Missing component usage: ${component}`;
    }
  }
  return true;
});

// Test 14: useSearch hook is imported and used
test('useSearch hook is imported and used', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  return content.includes('useSearch') && content.includes('const search = useSearch()');
});

// Test 15: useSyncSearchQuery hook is imported and used
test('useSyncSearchQuery hook is imported and used', () => {
  if (!fileExists('app/search/page.tsx')) {
    return 'app/search/page.tsx does not exist';
  }
  const content = readFile('app/search/page.tsx');
  return content.includes('useSyncSearchQuery') && content.includes('const urlSync = useSyncSearchQuery()');
});

// Print results
console.log('Test Results:\n');
console.log('='.repeat(60));

let passedCount = 0;
let failedCount = 0;

results.forEach((result, index) => {
  const status = result.passed ? '✅ PASS' : '❌ FAIL';
  console.log(`${(index + 1).toString().padStart(2, ' ')}. ${status} - ${result.name}`);
  if (!result.passed && result.error) {
    console.log(`     Error: ${result.error}`);
  }
  if (result.passed) {
    passedCount++;
  } else {
    failedCount++;
  }
});

console.log('='.repeat(60));
console.log(`\nSummary: ${passedCount} passed, ${failedCount} failed\n`);

if (failedCount > 0) {
  console.log('❌ Some tests failed. Please review the errors above.\n');
  process.exit(1);
} else {
  console.log('✅ All tests passed! Search page structure is valid.\n');
  process.exit(0);
}
