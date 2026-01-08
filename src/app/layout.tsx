import type { Metadata } from "next";
import { Assistant } from "next/font/google";
import "./globals.css";

const assistant = Assistant({
  subsets: ['latin', 'hebrew'],
  weight: ['200', '300', '400', '500', '600', '700', '800'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "SmarTrip - מערכת המלצות טיולים",
  description: "מערכת המלצות חכמה לטיולים מאורגנים - איילה גיאוגרפית",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="he" dir="rtl">
      <body className={`${assistant.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
