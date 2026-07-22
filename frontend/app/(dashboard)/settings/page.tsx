"use client";

import { useTheme } from "next-themes";
import { Monitor, Moon, Sun, Settings2, Server, Shield, Bell } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useHealthCheck } from "@/hooks/use-health";
import { cn } from "@/lib/utils";

function ThemeOption({
  value,
  current,
  icon: Icon,
  label,
  onClick,
}: {
  value: string;
  current: string | undefined;
  icon: React.ElementType;
  label: string;
  onClick: () => void;
}) {
  const isActive = current === value;
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200 flex-1",
        isActive
          ? "border-blue-500 bg-blue-600/10 text-blue-600"
          : "border-border hover:border-blue-300 text-muted-foreground"
      )}
    >
      <Icon className="h-6 w-6" />
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { data: health, isError } = useHealthCheck();

  const isHealthy = health?.status === "healthy" && health?.models_loaded;

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Settings2 className="h-6 w-6 text-blue-600" />
          Settings
        </h1>
        <p className="text-muted-foreground mt-1">Customize your experience and preferences.</p>
      </div>

      {/* Theme */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Appearance</CardTitle>
          <CardDescription>Choose how MDRP looks on your device</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <ThemeOption value="light" current={theme} icon={Sun} label="Light" onClick={() => setTheme("light")} />
            <ThemeOption value="dark" current={theme} icon={Moon} label="Dark" onClick={() => setTheme("dark")} />
            <ThemeOption value="system" current={theme} icon={Monitor} label="System" onClick={() => setTheme("system")} />
          </div>
        </CardContent>
      </Card>

      {/* API Status */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Server className="h-4 w-4 text-blue-600" />
            Backend Connection
          </CardTitle>
          <CardDescription>Status of the MDRP prediction API</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-muted/30 border border-border/50">
            <div className="flex items-center gap-3">
              <div className={cn(
                "h-3 w-3 rounded-full",
                isError ? "bg-red-500" : isHealthy ? "bg-emerald-500" : "bg-amber-500 animate-pulse"
              )} />
              <div>
                <p className="text-sm font-medium">
                  {isError ? "API Offline" : isHealthy ? "API Online" : "Connecting..."}
                </p>
                {health && (
                  <p className="text-xs text-muted-foreground">
                    Uptime: {Math.floor(health.uptime / 60)}m · v{health.version}
                  </p>
                )}
              </div>
            </div>
            <Badge variant={isError ? "destructive" : isHealthy ? "success" : "warning"}>
              {isError ? "Offline" : isHealthy ? "Healthy" : "Loading"}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Models Loaded</p>
              <p className="text-xs text-muted-foreground">ML prediction models status</p>
            </div>
            <Badge variant={health?.models_loaded ? "success" : "secondary"}>
              {health?.models_loaded ? "Ready" : "Not Ready"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Bell className="h-4 w-4 text-blue-600" />
            Notifications
          </CardTitle>
          <CardDescription>Manage how you receive updates</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { id: "prediction-complete", label: "Prediction Complete", desc: "Get notified when a prediction finishes" },
            { id: "pdf-parsed", label: "PDF Parsed", desc: "Get notified when lab report extraction completes" },
            { id: "risk-alerts", label: "High Risk Alerts", desc: "Alert me when risk scores exceed 70%" },
          ].map((item) => (
            <div key={item.id} className="flex items-center justify-between">
              <div>
                <Label htmlFor={item.id} className="text-sm cursor-pointer">{item.label}</Label>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
              <Switch id={item.id} defaultChecked={item.id === "risk-alerts"} />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Privacy */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Shield className="h-4 w-4 text-blue-600" />
            Privacy & Data
          </CardTitle>
          <CardDescription>Control how your data is used</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Store Prediction History</p>
              <p className="text-xs text-muted-foreground">Save predictions to your account for future reference</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div>
            <p className="text-sm font-medium mb-1">Data Disclaimer</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Your health data is encrypted and secured by Clerk. MDRP does not share your data 
              with third parties. Predictions are stored server-side and associated with your account. 
              You can delete predictions at any time from the History page.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
