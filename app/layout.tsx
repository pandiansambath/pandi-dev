// Local fonts, not next/font/google: Google downloads at build time and a
// flaky fetch turns a deploy red. These never change.
import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({ src: "./fonts/geist.woff2", variable: "--font-geist-sans", display: "swap" });
const geistMono = localFont({ src: "./fonts/geist-mono.woff2", variable: "--font-geist-mono", display: "swap" });
const fraunces = localFont({
  src: [
    { path: "./fonts/fraunces.woff2", style: "normal", weight: "100 900" },
    { path: "./fonts/fraunces-italic.woff2", style: "italic", weight: "100 900" },
  ],
  variable: "--font-fraunces",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Pandian Sambath",
  description: "System Engineer — Python, AWS and Generative AI. Chennai, India.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#07080c" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} ${fraunces.variable} h-full antialiased motion-safe:scroll-smooth`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
