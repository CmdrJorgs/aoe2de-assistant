import type { Metadata } from "next";
import { Source_Serif_4, JetBrains_Mono, Noto_Sans } from "next/font/google";
import "./globals.css";

const sourceSerif4 = Source_Serif_4({
  variable: "--font-source-serif",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

const notoSans = Noto_Sans({
  variable: "--font-noto-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "AoE2 Coach AI — War Room & Tactical Decision Engine",
  description: "Real-time AI tactical decision support and micro/macro coaching for Age of Empires II: Definitive Edition.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body
        className={`${sourceSerif4.variable} ${jetbrainsMono.variable} ${notoSans.variable} antialiased bg-background text-on-background min-h-screen relative selection:bg-gold-leaf selection:text-on-primary font-body-md`}
      >
        {children}
      </body>
    </html>
  );
}
