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

/**
 * Get dynamic image URL for a trip based on country name
 * 
 * Uses Pixabay API via backend endpoint. Backend handles caching and returns
 * the actual image URL. Falls back to placeholder if backend is unavailable.
 * 
 * @param countryName - Name of the country (e.g., "Samoa", "New Caledonia")
 * @param width - Image width (default: 1200)
 * @param height - Image height (default: 600)
 * @returns Image URL (backend endpoint that redirects to Pixabay or placeholder)
 */
export function getDynamicImageUrl(
  countryName: string | undefined,
  width: number = 1200,
  height: number = 600
): string {
  const country = countryName || 'landscape';
  const cacheKey = `${country.toLowerCase()}:${width}x${height}`;
  
  // Check client-side cache first (populated by prefetch)
  if (imageCache.has(cacheKey)) {
    const cachedUrl = imageCache.get(cacheKey);
    if (cachedUrl) {
      return cachedUrl;
    }
  }
  
  // Return backend endpoint URL with redirect flag
  // Backend will redirect (302) to actual Pixabay image or placeholder
  const encodedCountry = encodeURIComponent(country);
  const backendUrl = `${API_BASE_URL}/api/images/country/${encodedCountry}?width=${width}&height=${height}&redirect=true`;
  
  // Start async fetch to populate cache for next time (fire and forget)
  fetchCountryImage(country, width, height).catch(() => {
    // Silently fail - backend URL will work regardless
  });
  
  return backendUrl;
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
        // Trigger re-render by dispatching custom event (optional - can be used by components)
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('countryImageLoaded', {
            detail: { country: countryName, url: data.url }
          }));
        }
      }
    }
  } catch (error) {
    // Silently fail - placeholder is already being used
    console.debug(`[ImageUtils] Failed to fetch image for ${countryName}:`, error);
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

