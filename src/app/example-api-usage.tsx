/**
 * Example: How to use the API client in Next.js components
 * This file shows different usage patterns for fetching data from Flask backend
 */

'use client';

import { useEffect, useState } from 'react';
import { getCountries, getTrips, getTags, type Country, type Trip, type Tag } from '@/lib/api';

export function ExampleCountriesList() {
  const [countries, setCountries] = useState<Country[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCountries() {
      try {
        setLoading(true);
        const response = await getCountries();
        
        if (response.success && response.data) {
          setCountries(response.data);
        } else {
          setError(response.error || 'Failed to fetch countries');
        }
      } catch (err) {
        setError('An error occurred');
      } finally {
        setLoading(false);
      }
    }

    fetchCountries();
  }, []);

  if (loading) return <div>Loading countries...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {countries.map((country) => (
        <li key={country.id}>
          {country.name} ({country.nameHe}) - {country.continent}
        </li>
      ))}
    </ul>
  );
}

export function ExampleTripsList() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTrips() {
      const response = await getTrips({
        include_relations: true, // Include country, guide, and tags
        status: 'Open', // Only show open trips
      });

      if (response.success && response.data) {
        setTrips(response.data);
      }
      setLoading(false);
    }

    fetchTrips();
  }, []);

  if (loading) return <div>Loading trips...</div>;

  return (
    <div>
      {trips.map((trip) => (
        <div key={trip.id}>
          <h3>{trip.title} / {trip.titleHe}</h3>
          <p>Country: {trip.country?.name}</p>
          <p>Guide: {trip.guide?.name}</p>
          <p>Price: ₪{trip.price}</p>
          <p>Spots Left: {trip.spotsLeft}/{trip.maxCapacity}</p>
          <p>Status: {trip.status}</p>
          <p>Difficulty: {trip.difficultyLevel}/3</p>
          <div>
            Tags: {trip.tags?.map(tag => tag.nameHe).join(', ')}
          </div>
        </div>
      ))}
    </div>
  );
}

export function ExampleTagsFilter() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedTags, setSelectedTags] = useState<number[]>([]);
  const [trips, setTrips] = useState<Trip[]>([]);

  useEffect(() => {
    // Fetch all tags on mount
    async function fetchTags() {
      const response = await getTags();
      if (response.success && response.data) {
        setTags(response.data);
      }
    }
    fetchTags();
  }, []);

  useEffect(() => {
    // Fetch trips when selected tags change
    async function fetchFilteredTrips() {
      if (selectedTags.length === 0) return;

      // Note: The API currently supports filtering by one tag at a time
      // For multiple tags, you'd need to fetch and combine results
      const response = await getTrips({
        tag_id: selectedTags[0],
        include_relations: true,
      });

      if (response.success && response.data) {
        setTrips(response.data);
      }
    }

    fetchFilteredTrips();
  }, [selectedTags]);

  const toggleTag = (tagId: number) => {
    setSelectedTags(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    );
  };

  return (
    <div>
      <div>
        <h3>Filter by Trip Type:</h3>
        {tags.map(tag => (
          <label key={tag.id}>
            <input
              type="checkbox"
              checked={selectedTags.includes(tag.id)}
              onChange={() => toggleTag(tag.id)}
            />
            {tag.nameHe} ({tag.name})
          </label>
        ))}
      </div>

      <div>
        <h3>Filtered Trips:</h3>
        {trips.length === 0 ? (
          <p>No trips found. Select a tag to filter.</p>
        ) : (
          <ul>
            {trips.map(trip => (
              <li key={trip.id}>{trip.titleHe}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

/**
 * Example: Server Component (Next.js App Router)
 * Fetch data on the server for better SEO and performance
 */
export async function ExampleServerComponent() {
  // This runs on the server during build/request
  const response = await getCountries();
  const countries = response.data || [];

  return (
    <div>
      <h2>Countries (Server-Side Rendered)</h2>
      <ul>
        {countries.map((country) => (
          <li key={country.id}>
            {country.name} - {country.continent}
          </li>
        ))}
      </ul>
    </div>
  );
}


