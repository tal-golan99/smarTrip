/**
 * Results loading state - Spinner displayed while fetching search results.
 */
export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white mb-4"></div>
        <p className="text-white text-xl font-medium" dir="rtl">
          טוען תוצאות...
        </p>
      </div>
    </div>
  );
}

