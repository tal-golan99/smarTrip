/**
 * Results loading state - Spinner displayed while fetching search results.
 */
export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-[#076839] mb-4"></div>
        <p className="text-gray-600 text-xl font-medium" dir="rtl">
          טוען תוצאות...
        </p>
      </div>
    </div>
  );
}

