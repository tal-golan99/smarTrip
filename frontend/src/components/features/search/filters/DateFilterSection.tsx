/**
 * Date filter section - Month and year selection for trip dates.
 */
'use client';

import { Calendar } from 'lucide-react';
import { useMemo } from 'react';
import { useSearch } from '@/hooks/useSearch';
import { getAvailableMonths, getAvailableYears } from '@/lib/utils';

export function DateFilterSection() {
  const search = useSearch();
  
  // Available years (current and future only)
  const availableYears = useMemo(() => getAvailableYears(), []);
  
  // Available months based on selected year
  const availableMonths = useMemo(() => getAvailableMonths(search.filters.selectedYear), [search.filters.selectedYear]);

  return (
    <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
      <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
        <Calendar className="text-[#12acbe]" />
        מתי תרצה לנסוע?
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Year */}
        <div>
          <label className="block text-sm font-medium mb-2 text-right">שנה</label>
          <select
            value={search.filters.selectedYear}
            onChange={(e) => {
              e.preventDefault();
              e.stopPropagation();
              const newYear = e.target.value;
              // Reset month if current selection is no longer valid
              let newMonth = search.filters.selectedMonth;
              if (newYear !== 'all') {
                const newMonths = getAvailableMonths(newYear);
                if (newMonth !== 'all' && !newMonths.find(m => m.index.toString() === newMonth)) {
                  newMonth = 'all';
                }
              }
              search.setDate(newYear, newMonth);
            }}
            onFocus={(e) => e.stopPropagation()}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#ff9402] focus:outline-none text-right"
          >
            <option value="all">כל השנים</option>
            {availableYears.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        {/* Month */}
        <div>
          <label className="block text-sm font-medium mb-2 text-right">חודש</label>
          <select
            value={search.filters.selectedMonth}
            onChange={(e) => {
              e.preventDefault();
              e.stopPropagation();
              search.setDate(search.filters.selectedYear, e.target.value);
            }}
            onFocus={(e) => e.stopPropagation()}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-right"
          >
            <option value="all">כל השנה</option>
            {availableMonths.map(({ index, name }) => (
              <option key={index} value={String(index)}>
                {name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </section>
  );
}
