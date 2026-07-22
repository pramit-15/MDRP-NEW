import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { Toaster } from "sonner";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "MDRP — Multi Disease Risk Prediction Platform",
    template: "%s | MDRP",
  },
  description:
    "AI-powered multi-disease risk prediction platform for heart disease, diabetes, and kidney disease. Get personalized health insights backed by machine learning.",
  keywords: ["disease risk", "health prediction", "AI health", "diabetes risk", "heart disease", "kidney disease"],
  authors: [{ name: "MDRP Team" }],
  openGraph: {
    type: "website",
    title: "MDRP — Multi Disease Risk Prediction",
    description: "AI-powered health risk assessment platform",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#060d1f" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      signInUrl="/login"
      signUpUrl="/register"
      afterSignOutUrl="/"
    >
      <html lang="en" suppressHydrationWarning className={inter.variable}>
        <body className="min-h-screen bg-background font-sans antialiased">
          <ThemeProvider>
            <QueryProvider>
              {children}
              <Toaster
                position="top-right"
                richColors
                expand={false}
                duration={4000}
                toastOptions={{
                  classNames: {
                    toast: "rounded-xl border border-border shadow-xl",
                    title: "font-semibold",
                    description: "text-muted-foreground",
                  },
                }}
              />
            </QueryProvider>
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
