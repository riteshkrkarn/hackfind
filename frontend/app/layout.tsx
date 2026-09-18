import type { Metadata } from "next";
import { Atkinson_Hyperlegible, Chakra_Petch, Fragment_Mono } from "next/font/google";
import "./globals.css";

const chakra = Chakra_Petch({
  variable: "--font-chakra",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const atkinson = Atkinson_Hyperlegible({
  variable: "--font-atkinson",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const fragment = Fragment_Mono({
  variable: "--font-fragment",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "Hackfind",
  description:
    "Never miss the hackathon meant for you — filtered matches, deadlines, and reminders.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${chakra.variable} ${atkinson.variable} ${fragment.variable} min-h-screen antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
