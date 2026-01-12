import Link from 'next/link';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center px-4">
      <div className="text-center text-white max-w-md">
        <Image
          src="/images/logo/smartrip.png"
          alt="SmartTrip Logo"
          width={120}
          height={120}
          className="mx-auto mb-6"
        />
        <h1 className="text-6xl font-bold mb-4">404</h1>
        <h2 className="text-2xl font-semibold mb-4">הדף לא נמצא</h2>
        <p className="text-lg mb-8 text-white/90">
          הדף שחיפשת לא קיים או הועבר למיקום אחר.
        </p>
        <Link
          href="/"
          className="inline-block px-8 py-3 bg-white text-[#076839] rounded-xl font-semibold hover:bg-white/90 transition-colors"
        >
          חזרה לדף הבית
        </Link>
      </div>
    </div>
  );
}



