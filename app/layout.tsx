import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { ToastProvider } from "@/components/ui/toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Mission Control",
  description: "AI Agent Management Dashboard",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Mission Control",
  },
  themeColor: "#0d1117",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="apple-touch-icon" href="/icon-192.png" />
      </head>
      <body className={inter.className}>
        <ToastProvider>
          <div className="min-h-screen bg-[#080c14]">
            <Sidebar />
            <Header />
            {/* ml-0 on mobile (no sidebar), ml-[220px] on desktop */}
            {/* pb-20 on mobile for bottom nav clearance */}
            <main className="ml-0 md:ml-[220px] pt-14 pb-20 md:pb-6 p-4 md:p-6">
              {children}
            </main>
          </div>
        </ToastProvider>
      </body>
    </html>
  );
}
