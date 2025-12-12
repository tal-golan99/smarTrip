/**
 * Example React Component: Trip Recommendation UI
 * This demonstrates how to use the recommendation API in a Next.js component
 */

'use client';

import { useState, useEffect } from 'react';
import { 
  getTags, 
  getRecommendations, 
  type Tag, 
  type RecommendedTrip, 
  type RecommendationPreferences 
} from '@/lib/api';

export function TripRecommendationForm() {
  // State for tags
  const [typeTags, setTypeTags] = useState<Tag[]>([]);
  const [themeTags, setThemeTags] = useState<Tag[]>([]);
  
  // State for form inputs
  const [selectedType, setSelectedType] = useState<number | null>(null);
  const [selectedThemes, setSelectedThemes] = useState<number[]>([]);
  const [selectedContinent, setSelectedContinent] = useState<string>('');
  const [minDuration, setMinDuration] = useState<number>(7);
  const [maxDuration, setMaxDuration] = useState<number>(14);
  const [budget, setBudget] = useState<number>(10000);
  const [difficulty, setDifficulty] = useState<number>(2);
  const [startDate, setStartDate] = useState<string>('');
  
  // State for results
  const [recommendations, setRecommendations] = useState<RecommendedTrip[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load tags on mount
  useEffect(() => {
    async function fetchTags() {
      const response = await getTags();
      if (response.success && response.data) {
        const types = response.data.filter(t => t.category === 'Type');
        const themes = response.data.filter(t => t.category === 'Theme');
        setTypeTags(types);
        setThemeTags(themes);
      }
    }
    fetchTags();
  }, []);

  // Handle theme selection (max 3)
  const toggleTheme = (themeId: number) => {
    if (selectedThemes.includes(themeId)) {
      setSelectedThemes(selectedThemes.filter(id => id !== themeId));
    } else if (selectedThemes.length < 3) {
      setSelectedThemes([...selectedThemes, themeId]);
    }
  };

  // Submit recommendation request
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const preferences: RecommendationPreferences = {
      min_duration: minDuration,
      max_duration: maxDuration,
      budget: budget,
      difficulty: difficulty,
    };

    // Add optional fields only if set
    if (selectedType) preferences.preferred_type_id = selectedType;
    if (selectedThemes.length > 0) preferences.preferred_theme_ids = selectedThemes;
    if (selectedContinent) preferences.selected_continents = [selectedContinent];
    if (startDate) preferences.start_date = startDate;

    try {
      const response = await getRecommendations(preferences);
      if (response.success && response.data) {
        setRecommendations(response.data);
      } else {
        setError(response.error || 'Failed to get recommendations');
      }
    } catch (err) {
      setError('An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Find Your Perfect Trip</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Trip Style (TYPE) - Radio Buttons */}
        <div>
          <h2 className="text-xl font-semibold mb-3">Trip Style (Choose One)</h2>
          <div className="grid grid-cols-2 gap-3">
            {typeTags.map(tag => (
              <label key={tag.id} className="flex items-center space-x-2 p-3 border rounded cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="tripType"
                  value={tag.id}
                  checked={selectedType === tag.id}
                  onChange={() => setSelectedType(tag.id)}
                />
                <span>{tag.name} ({tag.nameHe})</span>
              </label>
            ))}
          </div>
        </div>

        {/* Trip Interests (THEME) - Checkboxes */}
        <div>
          <h2 className="text-xl font-semibold mb-3">
            Interests (Choose up to 3) - {selectedThemes.length}/3 selected
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {themeTags.map(tag => (
              <label 
                key={tag.id} 
                className={`flex items-center space-x-2 p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                  selectedThemes.includes(tag.id) ? 'bg-blue-50 border-blue-500' : ''
                } ${
                  selectedThemes.length >= 3 && !selectedThemes.includes(tag.id) ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedThemes.includes(tag.id)}
                  onChange={() => toggleTheme(tag.id)}
                  disabled={selectedThemes.length >= 3 && !selectedThemes.includes(tag.id)}
                />
                <span>{tag.name} ({tag.nameHe})</span>
              </label>
            ))}
          </div>
        </div>

        {/* Continent */}
        <div>
          <label className="block text-sm font-medium mb-2">Continent (Optional)</label>
          <select 
            value={selectedContinent} 
            onChange={(e) => setSelectedContinent(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Any Continent</option>
            <option value="Africa">Africa</option>
            <option value="Asia">Asia</option>
            <option value="Europe">Europe</option>
            <option value="North America">North America</option>
            <option value="South America">South America</option>
            <option value="Oceania">Oceania</option>
            <option value="Antarctica">Antarctica</option>
          </select>
        </div>

        {/* Duration */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Min Duration (days)</label>
            <input
              type="number"
              min="1"
              value={minDuration}
              onChange={(e) => setMinDuration(Number(e.target.value))}
              className="w-full p-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Max Duration (days)</label>
            <input
              type="number"
              min="1"
              value={maxDuration}
              onChange={(e) => setMaxDuration(Number(e.target.value))}
              className="w-full p-2 border rounded"
            />
          </div>
        </div>

        {/* Budget */}
        <div>
          <label className="block text-sm font-medium mb-2">Maximum Budget (ILS)</label>
          <input
            type="number"
            min="0"
            step="100"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="w-full p-2 border rounded"
          />
        </div>

        {/* Difficulty */}
        <div>
          <label className="block text-sm font-medium mb-2">Difficulty Level</label>
          <div className="flex space-x-4">
            {[1, 2, 3].map(level => (
              <label key={level} className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="difficulty"
                  value={level}
                  checked={difficulty === level}
                  onChange={() => setDifficulty(level)}
                />
                <span>{level === 1 ? 'Easy' : level === 2 ? 'Moderate' : 'Hard'}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Start Date */}
        <div>
          <label className="block text-sm font-medium mb-2">Earliest Start Date (Optional)</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded font-semibold hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Finding Trips...' : 'Get Recommendations'}
        </button>
      </form>

      {/* Error Display */}
      {error && (
        <div className="mt-6 p-4 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Results Display */}
      {recommendations.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Recommended Trips for You</h2>
          <div className="space-y-4">
            {recommendations.map(trip => (
              <div key={trip.id} className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="text-xl font-bold">{trip.title}</h3>
                    <p className="text-gray-600">{trip.titleHe}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-blue-600">
                      {trip.match_score}
                      <span className="text-sm text-gray-500">/100</span>
                    </div>
                    <div className="text-xs text-gray-500">Match Score</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                  <div>
                    <span className="font-semibold">Country:</span> {trip.country?.name}
                  </div>
                  <div>
                    <span className="font-semibold">Price:</span> ₪{trip.price}
                  </div>
                  <div>
                    <span className="font-semibold">Dates:</span> {trip.startDate} to {trip.endDate}
                  </div>
                  <div>
                    <span className="font-semibold">Available:</span> {trip.spotsLeft}/{trip.maxCapacity} spots
                  </div>
                </div>

                <div className="mb-3">
                  <div className="font-semibold text-sm mb-1">Why this trip matches:</div>
                  <div className="flex flex-wrap gap-2">
                    {trip.match_details.map((detail, idx) => (
                      <span key={idx} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                        {detail}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {trip.tags?.map(tag => (
                    <span 
                      key={tag.id} 
                      className={`text-xs px-2 py-1 rounded ${
                        tag.category === 'Type' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-purple-100 text-purple-800'
                      }`}
                    >
                      {tag.nameHe}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

