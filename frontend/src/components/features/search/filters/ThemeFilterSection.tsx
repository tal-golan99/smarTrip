'use client';

import { Sparkles, Compass } from 'lucide-react';
import { useSearch } from '@/hooks/useSearch';
import { useThemeTags } from '@/lib/dataStore';
import { THEME_TAG_ICONS } from '@/lib/dataStore';
import { TagCircle } from '@/components/ui/TagCircle';

interface SearchTag {
  id: number;
  name: string;
  nameHe: string;
  category: 'Type' | 'Theme';
}

export function ThemeFilterSection() {
  const search = useSearch();
  const { themeTags: themeTagsData, isLoading: isLoadingThemeTags } = useThemeTags();

  // Map DataStore types to SearchTag format for compatibility
  const themeTags: SearchTag[] = themeTagsData.map(t => ({
    id: t.id,
    name: t.name,
    nameHe: t.nameHe || t.name,
    category: 'Theme' as const
  }));

  return (
    <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
      <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
        <Sparkles className="text-[#12acbe]" />
        תחומי עניין
      </h2>
      <p className="text-sm text-gray-600 mb-3 md:mb-4 text-right">
        בחר עד 3 תחומי עניין ({search.filters.selectedThemes.length}/3)
      </p>

      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 md:gap-4">
        {themeTags.length > 0 ? themeTags.map(tag => {
          const Icon = THEME_TAG_ICONS[tag.name] || Compass;
          return (
            <TagCircle
              key={tag.id}
              label={tag.nameHe}
              isSelected={search.filters.selectedThemes.includes(tag.id)}
              onClick={() => search.toggleTheme(tag.id)}
              icon={Icon}
            />
          );
        }) : (
          <div className="col-span-full text-center text-gray-500 py-4 text-sm">
            {isLoadingThemeTags ? 'טוען נושאי טיול...' : 'לא ניתן לטעון נושאי טיול'}
          </div>
        )}
      </div>
    </section>
  );
}
