"use client";

import React, { useState, useEffect } from "react";
import { Bell, CheckCheck, AlertTriangle, FileText, CheckCircle2, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useUser } from "@clerk/nextjs";

interface NotificationItem {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: "info" | "warning" | "critical";
  is_read: boolean;
  data: Record<string, any>;
  created_at: string;
}

export function NotificationBell() {
  const { isSignedIn } = useUser();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isOpen, setIsOpen] = useState(false);

  const fetchNotifications = async () => {
    if (!isSignedIn) return;
    try {
      const res = await fetch("/api/v1/notifications?limit=10");
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.items || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (e) {
      console.debug("Failed to fetch notifications:", e);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000); // Polling every 15s
    return () => clearInterval(interval);
  }, [isSignedIn]);

  const markAsRead = async (id: string) => {
    try {
      await fetch(`/api/v1/notifications/${id}/read`, { method: "POST" });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (e) {
      console.debug("Failed to mark notification as read:", e);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch("/api/v1/notifications/read-all", { method: "POST" });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (e) {
      console.debug("Failed to mark all notifications as read:", e);
    }
  };

  if (!isSignedIn) return null;

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white shadow-sm ring-2 ring-background animate-pulse">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-80 sm:w-96 p-2 shadow-lg border-border">
        <div className="flex items-center justify-between px-2 py-1.5">
          <div className="flex items-center gap-1.5">
            <DropdownMenuLabel className="p-0 font-semibold text-sm">Notifications</DropdownMenuLabel>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="text-[10px] h-4 px-1.5 bg-red-500/10 text-red-600 dark:text-red-400">
                {unreadCount} new
              </Badge>
            )}
          </div>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={markAllAsRead}
              className="h-7 text-xs text-muted-foreground hover:text-foreground gap-1 px-2 cursor-pointer"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              Mark all read
            </Button>
          )}
        </div>

        <DropdownMenuSeparator className="my-1" />

        <div className="max-h-72 overflow-y-auto space-y-1 py-1">
          {notifications.length === 0 ? (
            <div className="py-6 text-center text-xs text-muted-foreground">
              No recent notifications
            </div>
          ) : (
            notifications.map((item) => {
              const isCritical = item.severity === "critical";
              const isWarning = item.severity === "warning";

              return (
                <div
                  key={item.id}
                  onClick={() => !item.is_read && markAsRead(item.id)}
                  className={`p-2.5 rounded-lg text-left transition-colors cursor-pointer flex items-start gap-2.5 ${
                    item.is_read
                      ? "hover:bg-muted/40 opacity-75"
                      : "bg-muted/60 hover:bg-muted font-medium"
                  }`}
                >
                  <div
                    className={`h-7 w-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                      isCritical
                        ? "bg-red-500/15 text-red-600 dark:text-red-400"
                        : isWarning
                        ? "bg-amber-500/15 text-amber-600 dark:text-amber-400"
                        : "bg-blue-500/15 text-blue-600 dark:text-blue-400"
                    }`}
                  >
                    {isCritical ? (
                      <ShieldAlert className="h-4 w-4" />
                    ) : isWarning ? (
                      <AlertTriangle className="h-4 w-4" />
                    ) : item.type === "pdf_parsed" ? (
                      <FileText className="h-4 w-4" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-semibold text-foreground truncate">
                        {item.title}
                      </span>
                      {!item.is_read && (
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-600 shrink-0" />
                      )}
                    </div>
                    <p className="text-[11px] text-muted-foreground leading-tight line-clamp-2 mt-0.5">
                      {item.message}
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
