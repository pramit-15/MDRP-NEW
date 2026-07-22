"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import { Bell, Moon, Sun, Search, Activity } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { useHealthCheck } from "@/hooks/use-health";
import { cn } from "@/lib/utils";

function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  const labelMap: Record<string, string> = {
    dashboard: "Dashboard",
    predictions: "Predictions",
    new: "New Prediction",
    history: "History",
    upload: "Upload PDF",
    profile: "Profile",
    settings: "Settings",
  };

  if (segments.length === 0) return null;

  return (
    <nav className="flex items-center gap-1.5 text-sm">
      {segments.map((seg, idx) => {
        const isLast = idx === segments.length - 1;
        const label = labelMap[seg] || seg.charAt(0).toUpperCase() + seg.slice(1);
        return (
          <span key={seg} className="flex items-center gap-1.5">
            {idx > 0 && <span className="text-muted-foreground">/</span>}
            <span className={cn(isLast ? "text-foreground font-medium" : "text-muted-foreground")}>
              {label}
            </span>
          </span>
        );
      })}
    </nav>
  );
}

function ApiStatus() {
  const { data, isError } = useHealthCheck();
  const isHealthy = data?.status === "healthy" && data?.models_loaded;

  return (
    <div className="flex items-center gap-2 text-xs">
      <div
        className={cn(
          "h-2 w-2 rounded-full",
          isError
            ? "bg-red-500"
            : isHealthy
            ? "bg-emerald-500 animate-pulse"
            : "bg-amber-500"
        )}
      />
      <span className="text-muted-foreground hidden sm:block">
        {isError ? "API Offline" : isHealthy ? "API Online" : "Connecting..."}
      </span>
    </div>
  );
}

export function Navbar() {
  const { user } = useUser();
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center border-b border-border bg-background/80 backdrop-blur-xl px-6 gap-4">
      {/* Mobile Logo */}
      <Link href="/dashboard" className="md:hidden flex items-center gap-2">
        <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
          <Activity className="h-4 w-4 text-white" />
        </div>
        <span className="font-bold">MDRP</span>
      </Link>

      {/* Breadcrumbs */}
      <div className="hidden md:block flex-1">
        <Breadcrumbs />
      </div>

      <div className="ml-auto flex items-center gap-3">
        <ApiStatus />

        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="text-muted-foreground"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>

        {/* User Avatar */}
        {user && (
          <Link href="/profile">
            {user.imageUrl ? (
              <img
                src={user.imageUrl}
                alt={user.fullName || "User"}
                className="h-8 w-8 rounded-full object-cover ring-2 ring-border hover:ring-blue-500 transition-all"
              />
            ) : (
              <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center ring-2 ring-border hover:ring-blue-500 transition-all">
                <span className="text-white text-xs font-bold">
                  {user.firstName?.[0] || "U"}
                </span>
              </div>
            )}
          </Link>
        )}
      </div>
    </header>
  );
}
