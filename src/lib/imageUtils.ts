/**
 * Image Utility Functions
 * ========================
 * 
 * Provides free image sources for trip images using Pixabay API via backend.
 * Uses client-side caching for performance.
 */

// Client-side cache for country images (in-memory)
// Key: "country:widthxheight", Value: image URL string
const imageCache = new Map<string, string>();

// API base URL (same as other API calls)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Detect if we're on localhost (function to evaluate at runtime)
function isLocalhost(): boolean {
  if (typeof window === 'undefined') {
    // Server-side: check API_BASE_URL
    return API_BASE_URL.includes('localhost');
  }
  // Client-side: check hostname and API_BASE_URL
  return (
    window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1' ||
    API_BASE_URL.includes('localhost')
  );
}

/**
 * Get dynamic image URL for a trip based on country name
 * 
 * Uses Pixabay API via backend endpoint. Backend handles caching and returns
 * the actual image URL. Uses different strategies for localhost vs production:
 * 
 * - **Production (HTTPS)**: Uses redirect URL for immediate display
 * - **Localhost (HTTP)**: Uses placeholder initially, updates when cache is populated
 * 
 * @param countryName - Name of the country (e.g., "Samoa", "New Caledonia")
 * @param width - Image width (default: 1200)
 * @param height - Image height (default: 600)
 * @returns Backend redirect URL (production) or placeholder (localhost) or cached Pixabay URL
 */
export function getDynamicImageUrl(
  countryName: string | undefined,
  width: number = 1200,
  height: number = 600
): string {
  const country = countryName || 'landscape';
  const cacheKey = `${country.toLowerCase()}:${width}x${height}`;
  
  // Check client-side cache first (populated by prefetch or previous fetch)
  // If we have cached Pixabay URL (not placeholder), use it directly
  if (imageCache.has(cacheKey)) {
    const cachedUrl = imageCache.get(cacheKey);
    if (cachedUrl && !cachedUrl.includes('placehold.co')) {
      return cachedUrl;
    }
  }
  
  // Start async fetch to populate cache (fire and forget)
  // This will populate cache with real Pixabay URL for next render
  fetchCountryImage(country, width, height).catch(() => {
    // Silently fail - will use fallback
  });
  
  // On localhost (HTTP), use placeholder initially
  // Components will update when async fetch completes (via event listener)
  // This avoids mixed content issues with HTTP → HTTPS redirects
  if (isLocalhost()) {
    const encodedCountry = encodeURIComponent(country);
    return `https://placehold.co/${width}x${height}/4A90E2/FFFFFF?text=${encodedCountry}`;
  }
  
  // On production (HTTPS), use redirect URL for immediate display
  // Backend will redirect (302) to actual Pixabay image URL or placeholder
  // HTTPS redirects work perfectly in production
  const encodedCountry = encodeURIComponent(country);
  return `${API_BASE_URL}/api/images/country/${encodedCountry}?width=${width}&height=${height}&redirect=true`;
}

/**
 * Fetch country image from backend and cache it
 * Called asynchronously to populate cache
 */
async function fetchCountryImage(
  countryName: string,
  width: number,
  height: number
): Promise<void> {
  const country = countryName || 'landscape';
  const cacheKey = `${country.toLowerCase()}:${width}x${height}`;
  const encodedCountry = encodeURIComponent(country);
  
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/images/country/${encodedCountry}?width=${width}&height=${height}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (response.ok) {
      const data = await response.json();
      if (data.success && data.url) {
        // Cache the URL
        imageCache.set(cacheKey, data.url);
        console.log(`[ImageUtils] Successfully loaded image for ${countryName}:`, data.url);
        // Trigger re-render by dispatching custom event (optional - can be used by components)
        if (typeof window !== 'undefined') {
          const event = new CustomEvent('countryImageLoaded', {
            detail: { country: countryName, url: data.url, cacheKey }
          });
          console.log(`[ImageUtils] Dispatching countryImageLoaded event for: ${countryName}`);
          window.dispatchEvent(event);
        }
      } else {
        console.warn(`[ImageUtils] Backend returned success=false for ${countryName}:`, data);
      }
    } else {
      console.warn(`[ImageUtils] Backend returned status ${response.status} for ${countryName}`);
      const errorText = await response.text().catch(() => 'Unable to read error');
      console.warn(`[ImageUtils] Error response:`, errorText);
    }
  } catch (error) {
    // Log error for debugging (especially on localhost)
    console.warn(`[ImageUtils] Failed to fetch image for ${countryName}:`, error);
    if (error instanceof Error) {
      console.warn(`[ImageUtils] Error details: ${error.message}`);
    }
    console.warn(`[ImageUtils] Backend URL: ${API_BASE_URL}/api/images/country/${encodedCountry}`);
  }
}

/**
 * Pre-fetch image for a country (useful for prefetching before display)
 * Returns the image URL once fetched, or placeholder if fetch fails
 */
export async function prefetchCountryImage(
  countryName: string | undefined,
  width: number = 1200,
  height: number = 600
): Promise<string> {
  const country = countryName || 'landscape';
  const cacheKey = `${country.toLowerCase()}:${width}x${height}`;
  
  // Check cache first
  if (imageCache.has(cacheKey)) {
    const cachedUrl = imageCache.get(cacheKey);
    if (cachedUrl) {
      return cachedUrl;
    }
  }
  
  // Fetch from backend
  await fetchCountryImage(country, width, height);
  
  // Return cached URL or placeholder
  if (imageCache.has(cacheKey)) {
    const cachedUrl = imageCache.get(cacheKey);
    if (cachedUrl) {
      return cachedUrl;
    }
  }
  
  // Fallback to placeholder (using placehold.co as it's more reliable)
  const encodedCountry = encodeURIComponent(country);
  return `https://placehold.co/${width}x${height}/4A90E2/FFFFFF?text=${encodedCountry}`;
}

/**
 * Get image URL with fallback chain
 * Tries multiple sources if one fails
 * 
 * @param countryName - Name of the country
 * @param width - Image width
 * @param height - Image height
 * @returns Array of image URLs to try (in order)
 */
export function getImageUrlFallbacks(
  countryName: string | undefined,
  width: number = 1200,
  height: number = 600
): string[] {
  const country = countryName || 'landscape';
  const cacheKey = `${country.toLowerCase()}:${width}x${height}`;
  const encodedCountry = encodeURIComponent(country);
  
  const urls: string[] = [];
  
  // Add cached URL if available
  if (imageCache.has(cacheKey)) {
    const cachedUrl = imageCache.get(cacheKey);
    if (cachedUrl) {
      urls.push(cachedUrl);
    }
  }
  
  // Always include placeholder as final fallback (using placehold.co as it's more reliable)
  urls.push(`https://placehold.co/${width}x${height}/4A90E2/FFFFFF?text=${encodedCountry}`);
  
  return urls;
}


