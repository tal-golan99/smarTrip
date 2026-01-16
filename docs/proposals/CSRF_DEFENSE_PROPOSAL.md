# CSRF Defense Implementation Proposal

**Author:** Security Review  
**Date:** January 2026  
**Status:** Proposal - Pending Implementation

---

## Executive Summary

This document proposes a comprehensive Cross-Site Request Forgery (CSRF) defense strategy for the SmartTrip application. Currently, the application lacks CSRF protection, which poses a security risk for state-changing operations. This proposal outlines a multi-layered defense approach suitable for a JWT-based authentication system with a Next.js frontend and Flask backend.

---

## Current State Analysis

### Authentication Architecture

The SmartTrip application uses:
- **Frontend**: Next.js 14 with Supabase authentication
- **Backend**: Flask 3.0 with JWT verification via `SUPABASE_JWT_SECRET`
- **Auth Method**: Bearer token authentication (`Authorization: Bearer <jwt>`)
- **CORS**: Configured via `flask-cors` with `supports_credentials: True`

### Vulnerable Endpoints

The following POST endpoints are currently vulnerable to CSRF attacks:

1. **`POST /api/v2/recommendations`** - Trip recommendations (state-changing search)
2. **`POST /api/events/session/start`** - Analytics session tracking
3. **`POST /api/events/events`** - Single event tracking
4. **`POST /api/events/events/batch`** - Batch event tracking
5. **`POST /api/events/user/identify`** - User identification
6. **`POST /api/evaluation/run`** - Evaluation runs (if authenticated)

### Current Security Measures

**Existing Protections:**
- CORS configured with allowed origins
- JWT token verification for authenticated requests
- Bearer token authentication (not cookie-based)

**Missing Protections:**
- No CSRF token validation
- No SameSite cookie attributes (not applicable since using JWT)
- No Origin/Referer header validation
- No double-submit cookie pattern

### Why CSRF Protection is Needed

Even though the application uses JWT tokens in Authorization headers (which browsers don't automatically send), CSRF protection is still important because:

1. **Future Cookie-Based Features**: If the application adds cookie-based authentication or session management, CSRF becomes critical
2. **Browser Extensions**: Some browser extensions can inject Authorization headers
3. **Same-Origin Policy Limitations**: CORS allows cross-origin requests from allowed origins
4. **Best Practice**: Defense in depth - multiple layers of security
5. **Compliance**: Many security standards require CSRF protection for state-changing operations

---

## CSRF Attack Scenarios

### Scenario 1: Malicious Website Attack

**Attack Vector:**
```html
<!-- Attacker's website: evil.com -->
<form action="https://your-app.vercel.app/api/v2/recommendations" method="POST">
  <input type="hidden" name="selected_countries" value="[999]">
  <input type="hidden" name="budget" value="999999">
  <!-- ... other malicious data ... -->
</form>
<script>document.forms[0].submit();</script>
```

**Impact:** If user is logged in and has a valid JWT, browser may send the request with credentials, potentially triggering unwanted actions.

### Scenario 2: Cross-Site Form Submission

**Attack Vector:**
```html
<!-- Attacker tricks user into visiting their site -->
<img src="https://your-app.vercel.app/api/events/events/batch" 
     style="display:none">
```

**Impact:** GET requests converted to POST via form submission could trigger analytics events or other state changes.

### Scenario 3: Future Cookie-Based Auth

**Future Risk:** If the application migrates to cookie-based authentication or adds session cookies, CSRF becomes a critical vulnerability.

---

## Proposed Solution: Multi-Layered CSRF Defense

### Defense Strategy Overview

We propose implementing a **three-layer defense strategy**:

1. **Primary Defense**: CSRF Token Validation (Double-Submit Cookie Pattern)
2. **Secondary Defense**: Origin/Referer Header Validation
3. **Tertiary Defense**: SameSite Cookie Attributes (for future cookie-based features)

### Why Double-Submit Cookie Pattern?

The Double-Submit Cookie pattern is ideal for this application because:

- **JWT-Compatible**: Works alongside JWT authentication
- **Stateless**: No server-side session storage required
- **Simple**: Easy to implement and maintain
- **Effective**: Prevents CSRF attacks effectively
- **Next.js Compatible**: Works well with Next.js API routes and client-side rendering

---

## Implementation Plan

### Phase 1: Backend CSRF Token Generation and Validation

#### 1.1 Create CSRF Token Utility Module

**File:** `backend/app/core/csrf.py`

**Responsibilities:**
- Generate cryptographically secure CSRF tokens
- Validate tokens against cookies
- Provide decorator for protected endpoints

**Implementation:**

```python
import secrets
import hmac
import hashlib
from functools import wraps
from flask import request, jsonify, g
from app.core.config import get_config

# CSRF token length (32 bytes = 64 hex characters)
CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = 'XSRF-TOKEN'
CSRF_HEADER_NAME = 'X-CSRF-Token'


def generate_csrf_token() -> str:
    """
    Generate a cryptographically secure CSRF token.
    Returns a hex-encoded random token.
    """
    return secrets.token_hex(CSRF_TOKEN_LENGTH)


def validate_csrf_token(token: str, cookie_token: str) -> bool:
    """
    Validate CSRF token using constant-time comparison.
    Compares the provided token with the cookie token.
    
    Args:
        token: Token from request header
        cookie_token: Token from cookie
        
    Returns:
        True if tokens match, False otherwise
    """
    if not token or not cookie_token:
        return False
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(token, cookie_token)


def get_csrf_token_from_request() -> tuple[str | None, str | None]:
    """
    Extract CSRF token from request header and cookie.
    
    Returns:
        Tuple of (header_token, cookie_token)
    """
    header_token = request.headers.get(CSRF_HEADER_NAME)
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    return header_token, cookie_token


def require_csrf(f):
    """
    Decorator to require CSRF token validation for state-changing operations.
    
    Usage:
        @api_v2_bp.route('/recommendations', methods=['POST'])
        @require_csrf
        def get_recommendations():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF check for GET, HEAD, OPTIONS requests
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)
        
        # Skip CSRF check if no authentication is required
        # (CSRF is primarily for authenticated requests)
        user = getattr(g, 'current_user', None)
        if not user:
            # For guest requests, we can optionally skip CSRF
            # or require it for all state-changing operations
            # For now, we'll require it for all POST/PUT/DELETE
            pass
        
        header_token, cookie_token = get_csrf_token_from_request()
        
        if not header_token or not cookie_token:
            return jsonify({
                'success': False,
                'error': 'CSRF token missing'
            }), 403
        
        if not validate_csrf_token(header_token, cookie_token):
            return jsonify({
                'success': False,
                'error': 'Invalid CSRF token'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
```

#### 1.2 Create CSRF Token Endpoint

**File:** `backend/app/api/system/routes.py` (add to existing file)

**New Endpoint:**

```python
@system_bp.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    Generate and return a CSRF token.
    Token is set as a cookie and also returned in response body.
    
    Frontend should:
    1. Call this endpoint on app initialization
    2. Store the token from response body
    3. Include token in X-CSRF-Token header for all POST/PUT/DELETE requests
    4. Cookie is automatically sent by browser
    """
    from app.core.csrf import generate_csrf_token
    
    token = generate_csrf_token()
    
    response = jsonify({
        'success': True,
        'csrf_token': token
    })
    
    # Set cookie with SameSite=None for cross-origin support
    # Secure=True required when SameSite=None
    response.set_cookie(
        'XSRF-TOKEN',
        token,
        httponly=False,  # Must be readable by JavaScript
        samesite='Lax',   # Lax allows GET requests from other sites but protects POST
        secure=True,      # Require HTTPS in production
        max_age=86400    # 24 hours
    )
    
    return response
```

#### 1.3 Apply CSRF Protection to Vulnerable Endpoints

**Files to Update:**

1. **`backend/app/api/v2/routes.py`**
   - Add `@require_csrf` decorator to `/recommendations` POST endpoint

2. **`backend/app/api/events/routes.py`**
   - Add `@require_csrf` decorator to all POST endpoints:
     - `/session/start`
     - `/events`
     - `/events/batch`
     - `/user/identify`

3. **`backend/app/api/analytics/routes.py`**
   - Add `@require_csrf` decorator to `/evaluation/run` POST endpoint

**Example Update:**

```python
from app.core.csrf import require_csrf

@api_v2_bp.route('/recommendations', methods=['POST'])
@require_csrf
@optional_auth
def get_recommendations():
    # Existing implementation
    ...
```

### Phase 2: Frontend CSRF Token Management

#### 2.1 Create CSRF Token Service

**File:** `frontend/src/services/csrf.ts`

**Responsibilities:**
- Fetch CSRF token from backend
- Store token in memory
- Provide token for API requests
- Handle token refresh

**Implementation:**

```typescript
/**
 * CSRF Token Management Service
 * 
 * Handles fetching, storing, and providing CSRF tokens for API requests.
 * Tokens are stored in memory and automatically included in request headers.
 */

const CSRF_TOKEN_ENDPOINT = '/api/csrf-token';
const CSRF_HEADER_NAME = 'X-CSRF-Token';
const CSRF_COOKIE_NAME = 'XSRF-TOKEN';

let csrfToken: string | null = null;
let tokenFetchPromise: Promise<string> | null = null;

/**
 * Fetch CSRF token from backend.
 * Token is set as a cookie automatically by the backend.
 * 
 * @returns Promise resolving to CSRF token
 */
async function fetchCsrfToken(): Promise<string> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  
  try {
    const response = await fetch(`${apiUrl}${CSRF_TOKEN_ENDPOINT}`, {
      method: 'GET',
      credentials: 'include', // Include cookies
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch CSRF token: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (!data.success || !data.csrf_token) {
      throw new Error('Invalid CSRF token response');
    }
    
    return data.csrf_token;
  } catch (error) {
    console.error('[CSRF] Failed to fetch token:', error);
    throw error;
  }
}

/**
 * Get CSRF token, fetching if necessary.
 * Uses a promise cache to prevent multiple simultaneous requests.
 * 
 * @returns Promise resolving to CSRF token
 */
export async function getCsrfToken(): Promise<string | null> {
  // Return cached token if available
  if (csrfToken) {
    return csrfToken;
  }
  
  // Return existing fetch promise if in progress
  if (tokenFetchPromise) {
    return tokenFetchPromise;
  }
  
  // Start new fetch
  tokenFetchPromise = fetchCsrfToken()
    .then((token) => {
      csrfToken = token;
      tokenFetchPromise = null;
      return token;
    })
    .catch((error) => {
      tokenFetchPromise = null;
      console.error('[CSRF] Token fetch failed:', error);
      return null;
    });
  
  return tokenFetchPromise;
}

/**
 * Get CSRF token synchronously (if already cached).
 * Returns null if token not yet fetched.
 * 
 * @returns CSRF token or null
 */
export function getCsrfTokenSync(): string | null {
  return csrfToken;
}

/**
 * Clear cached CSRF token.
 * Forces next getCsrfToken() call to fetch a new token.
 */
export function clearCsrfToken(): void {
  csrfToken = null;
  tokenFetchPromise = null;
}

/**
 * Get CSRF header for API requests.
 * 
 * @returns Object with CSRF header, or empty object if token unavailable
 */
export async function getCsrfHeader(): Promise<Record<string, string>> {
  const token = await getCsrfToken();
  
  if (!token) {
    return {};
  }
  
  return {
    [CSRF_HEADER_NAME]: token,
  };
}

/**
 * Initialize CSRF token on app startup.
 * Should be called once when the app initializes.
 * 
 * @returns Promise resolving when token is fetched
 */
export async function initializeCsrfToken(): Promise<void> {
  try {
    await getCsrfToken();
  } catch (error) {
    console.warn('[CSRF] Failed to initialize token:', error);
  }
}
```

#### 2.2 Update API Client to Include CSRF Token

**File:** `frontend/src/lib/api.ts`

**Update `getAuthHeaders` function:**

```typescript
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const headers: Record<string, string> = {};
    
    // Add CSRF token for state-changing requests
    if (typeof window !== 'undefined') {
      const { getCsrfHeader } = await import('../services/csrf');
      const csrfHeaders = await getCsrfHeader();
      Object.assign(headers, csrfHeaders);
    }
    
    // Add JWT token if authenticated
    if (typeof window === 'undefined') {
      return headers; // SSR: no auth
    }
    
    const { getAccessToken } = await import('./supabaseClient');
    const token = await getAccessToken();
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  } catch (error) {
    if (error instanceof Error && !error.message.includes('Supabase not configured')) {
      console.warn('[API] Could not get auth headers:', error);
    }
  }
  
  return {};
}
```

**Update `apiFetch` to ensure credentials are included:**

```typescript
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const authHeaders = await getAuthHeaders();
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      credentials: 'include', // Include cookies for CSRF token
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...options?.headers,
      },
      ...options,
    });

    // Handle CSRF token errors
    if (response.status === 403) {
      const data = await response.json();
      if (data.error === 'CSRF token missing' || data.error === 'Invalid CSRF token') {
        // Clear cached token and retry once
        const { clearCsrfToken, getCsrfHeader } = await import('../services/csrf');
        clearCsrfToken();
        const newCsrfHeaders = await getCsrfHeader();
        
        if (newCsrfHeaders['X-CSRF-Token']) {
          // Retry with new token
          const retryHeaders = await getAuthHeaders();
          const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              ...retryHeaders,
              ...options?.headers,
            },
            ...options,
          });
          
          if (retryResponse.ok) {
            const retryData = await retryResponse.json();
            return retryData;
          }
        }
      }
    }
    
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}
```

#### 2.3 Initialize CSRF Token on App Load

**File:** `frontend/src/app/layout.tsx` or root component

**Add initialization:**

```typescript
'use client';

import { useEffect } from 'react';
import { initializeCsrfToken } from '@/services/csrf';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Initialize CSRF token on app load
    initializeCsrfToken().catch((error) => {
      console.warn('[App] Failed to initialize CSRF token:', error);
    });
  }, []);

  // ... rest of layout
}
```

### Phase 3: Additional Security Headers

#### 3.1 Add Origin/Referer Validation (Secondary Defense)

**File:** `backend/app/core/csrf.py` (add to existing file)

**Add validation function:**

```python
import os
from urllib.parse import urlparse

def validate_origin_header() -> bool:
    """
    Validate Origin or Referer header as secondary CSRF defense.
    
    Returns:
        True if origin is valid, False otherwise
    """
    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')
    
    # Get allowed origins from environment
    allowed_origins_str = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]
    
    # Check Origin header first (more reliable)
    if origin:
        if origin in allowed_origins:
            return True
    
    # Fallback to Referer header
    if referer:
        try:
            referer_origin = urlparse(referer).scheme + '://' + urlparse(referer).netloc
            if referer_origin in allowed_origins:
                return True
        except Exception:
            pass
    
    # Allow if no origin/referer (same-origin requests)
    # This handles direct API calls and same-origin requests
    if not origin and not referer:
        return True
    
    return False
```

**Update `require_csrf` decorator:**

```python
def require_csrf(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)
        
        # Primary defense: CSRF token validation
        header_token, cookie_token = get_csrf_token_from_request()
        
        if not header_token or not cookie_token:
            return jsonify({
                'success': False,
                'error': 'CSRF token missing'
            }), 403
        
        if not validate_csrf_token(header_token, cookie_token):
            return jsonify({
                'success': False,
                'error': 'Invalid CSRF token'
            }), 403
        
        # Secondary defense: Origin/Referer validation
        if not validate_origin_header():
            return jsonify({
                'success': False,
                'error': 'Invalid origin'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### Phase 4: Testing and Validation

#### 4.1 Unit Tests

**File:** `backend/tests/unit/test_csrf.py`

**Test Cases:**
- Token generation produces valid tokens
- Token validation works correctly
- Invalid tokens are rejected
- Missing tokens are rejected
- Constant-time comparison prevents timing attacks
- Origin validation works correctly

#### 4.2 Integration Tests

**File:** `backend/tests/integration/test_csrf_protection.py`

**Test Cases:**
- CSRF token endpoint returns token and sets cookie
- Protected endpoints require CSRF token
- Protected endpoints reject requests without token
- Protected endpoints reject requests with invalid token
- Token refresh works correctly
- CORS and CSRF work together

#### 4.3 Manual Testing Checklist

- [ ] CSRF token is fetched on app load
- [ ] CSRF token is included in POST requests
- [ ] Requests without CSRF token are rejected
- [ ] Requests with invalid CSRF token are rejected
- [ ] Token refresh works after expiration
- [ ] CORS still works correctly
- [ ] JWT authentication still works correctly
- [ ] Guest requests work correctly (if CSRF required for guests)

---

## Configuration

### Environment Variables

**Backend (`backend/.env`):**

```env
# Existing variables
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# CSRF configuration (optional - defaults provided)
CSRF_TOKEN_LENGTH=32
CSRF_COOKIE_NAME=XSRF-TOKEN
CSRF_HEADER_NAME=X-CSRF-Token
CSRF_COOKIE_MAX_AGE=86400  # 24 hours
```

**Frontend (`frontend/.env.local`):**

```env
# Existing variables
NEXT_PUBLIC_API_URL=http://localhost:5000

# CSRF is handled automatically, no configuration needed
```

### Production Considerations

1. **HTTPS Required**: CSRF cookies with `SameSite=None` require `Secure=True`, which requires HTTPS
2. **Cookie Domain**: Ensure cookie domain matches your frontend domain
3. **Token Expiration**: Consider shorter expiration times for higher security
4. **Token Rotation**: Implement token rotation on sensitive operations

---

## Migration Strategy

### Step 1: Backend Implementation (Non-Breaking)

1. Add CSRF token generation endpoint
2. Add CSRF validation decorator (not yet applied)
3. Test token generation and validation

### Step 2: Frontend Implementation

1. Add CSRF token service
2. Update API client to include CSRF tokens
3. Initialize CSRF token on app load
4. Test token fetching and inclusion

### Step 3: Gradual Rollout

1. Apply CSRF protection to one endpoint (e.g., `/events/batch`)
2. Monitor for errors
3. Gradually apply to other endpoints
4. Monitor error rates and user impact

### Step 4: Full Protection

1. Apply CSRF protection to all POST/PUT/DELETE endpoints
2. Remove any bypass mechanisms
3. Monitor and adjust as needed

---

## Security Considerations

### Token Storage

- **Cookie**: Stored in `XSRF-TOKEN` cookie (not HttpOnly, readable by JavaScript)
- **Memory**: Token also stored in frontend memory for header inclusion
- **No Server Storage**: Stateless approach - no server-side session storage

### Token Security

- **Cryptographically Secure**: Uses `secrets.token_hex()` for generation
- **Constant-Time Comparison**: Uses `hmac.compare_digest()` to prevent timing attacks
- **Token Length**: 32 bytes (64 hex characters) provides sufficient entropy

### Cookie Security

- **SameSite=Lax**: Protects against most CSRF attacks while allowing GET requests
- **Secure=True**: Requires HTTPS in production
- **HttpOnly=False**: Required for JavaScript to read token (by design of double-submit pattern)

### Limitations

1. **XSS Vulnerability**: If XSS exists, attacker can read CSRF token from cookie
2. **Subdomain Attacks**: If subdomains share cookies, CSRF protection may be bypassed
3. **Browser Extensions**: Malicious extensions could potentially read tokens

### Mitigations

1. **XSS Prevention**: Implement Content Security Policy (CSP) headers
2. **Subdomain Isolation**: Use separate cookie domains for different subdomains
3. **Additional Layers**: Origin/Referer validation provides secondary defense

---

## Performance Impact

### Backend

- **Token Generation**: Negligible (< 1ms)
- **Token Validation**: Negligible (< 1ms)
- **Cookie Parsing**: Minimal overhead
- **Overall Impact**: < 2ms per request

### Frontend

- **Token Fetch**: One-time on app load (~50-100ms)
- **Token Storage**: In-memory, no overhead
- **Header Addition**: Negligible
- **Overall Impact**: Minimal, one-time cost

---

## Alternative Approaches Considered

### 1. Synchronizer Token Pattern

**Pros:**
- Strong security
- Server-side validation

**Cons:**
- Requires server-side session storage
- Not stateless
- More complex implementation
- Doesn't fit JWT-based architecture

**Decision:** Rejected - doesn't fit stateless JWT architecture

### 2. Custom Header Pattern

**Pros:**
- Simple implementation
- No cookies needed

**Cons:**
- CORS preflight required
- Less secure (can be bypassed with CORS misconfiguration)
- Doesn't work with all browsers

**Decision:** Rejected - less secure, CORS complications

### 3. Origin/Referer Header Only

**Pros:**
- Simple
- No tokens needed

**Cons:**
- Can be spoofed in some scenarios
- Referer can be blocked by privacy tools
- Less reliable

**Decision:** Rejected - insufficient as primary defense

### 4. Double-Submit Cookie Pattern (Selected)

**Pros:**
- Stateless (fits JWT architecture)
- Simple implementation
- Effective CSRF protection
- Works with CORS
- No server-side storage

**Cons:**
- Vulnerable to XSS (but so are other patterns)
- Requires cookie support

**Decision:** Selected - best fit for current architecture

---

## Future Enhancements

### 1. Token Rotation

Implement automatic token rotation:
- Rotate tokens periodically
- Rotate tokens after sensitive operations
- Rotate tokens on logout

### 2. Per-Endpoint Tokens

Use different tokens for different endpoint groups:
- Analytics endpoints: shorter-lived tokens
- User data endpoints: longer-lived tokens
- Admin endpoints: separate token system

### 3. CSRF Token in JWT

Embed CSRF token in JWT payload:
- Single token for both authentication and CSRF
- Reduces token management complexity
- Requires JWT refresh on CSRF token change

### 4. Content Security Policy

Implement CSP headers to prevent XSS:
- Prevents XSS attacks that could steal CSRF tokens
- Complements CSRF protection
- Should be implemented alongside CSRF

---

## Rollback Plan

If issues arise during implementation:

1. **Immediate Rollback**: Remove `@require_csrf` decorators from endpoints
2. **Partial Rollback**: Keep token generation but make validation optional
3. **Configuration Toggle**: Add `CSRF_ENABLED` environment variable to disable CSRF protection

---

## Success Metrics

### Security Metrics

- [ ] All POST/PUT/DELETE endpoints protected
- [ ] Zero CSRF vulnerabilities in security audits
- [ ] Successful CSRF attack simulation blocked

### Performance Metrics

- [ ] Token generation < 1ms
- [ ] Token validation < 1ms
- [ ] No significant increase in API response times
- [ ] Frontend initialization time increase < 100ms

### User Experience Metrics

- [ ] No increase in API error rates
- [ ] No user-reported issues
- [ ] Seamless token refresh

---

## References

- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Double-Submit Cookie Pattern](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#double-submit-cookie)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/3.0.x/security/)
- [Next.js Security Headers](https://nextjs.org/docs/advanced-features/security-headers)

---

## Appendix: Code Examples

### Complete Backend CSRF Module

See Phase 1.1 for complete implementation.

### Complete Frontend CSRF Service

See Phase 2.1 for complete implementation.

### Example Protected Endpoint

```python
from app.core.csrf import require_csrf
from app.core.auth_supabase import optional_auth

@api_v2_bp.route('/recommendations', methods=['POST'])
@require_csrf
@optional_auth
def get_recommendations():
    """
    Get trip recommendations.
    Protected by CSRF token validation.
    """
    # CSRF token already validated by decorator
    # JWT authentication handled by optional_auth decorator
    # Implementation continues...
    pass
```

### Example Frontend API Call

```typescript
import { getRecommendations } from '@/lib/api';

// CSRF token automatically included by apiFetch
const result = await getRecommendations({
  selected_countries: [1, 5],
  budget: 12000,
  // ... other parameters
});
```

---

## Conclusion

This CSRF defense proposal provides a comprehensive, multi-layered approach to protecting the SmartTrip application against Cross-Site Request Forgery attacks. The Double-Submit Cookie pattern is well-suited for the JWT-based authentication architecture and provides effective protection with minimal performance impact.

Implementation should proceed in phases, with careful testing and monitoring at each stage. The proposed solution is production-ready and follows security best practices while maintaining compatibility with the existing application architecture.
