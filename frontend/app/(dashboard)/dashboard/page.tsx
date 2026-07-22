"use client";

import { useUser } from "@clerk/nextjs";
import Link from "next/link";
import {
  PlusCircle,
  Upload,
  History,
  TrendingUp,
  TrendingDown,
  Heart,
  Activity,
  Brain,
  AlertTriangle,
  ArrowRight,
  Calendar,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton, SkeletonCard } from "@/components/ui/skeleton";
import { useHistory } from "@/hooks/use-predictions";
import { formatRelativeTime, getCompositeScore } from "@/lib/utils";
import { getRiskLevel, getRiskBgColor, getRiskLabel } from "@/types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
  Area,
  AreaChart,
} from "recharts";

// ─── Stat Card ────────────────────────────────────────────────────────────────

function StatCard({
  icon: Icon,
  title,
  value,
  subtitle,
  trend,
  color,
  bg,
}: {
  icon: React.ElementType;
  title: string;
  value: string | number;
  subtitle: string;
  trend?: { value: number; label: string };
  color: string;
  bg: string;
}) {
  return (
    <Card className="card-hover">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className={`inline-flex h-11 w-11 items-center justify-center rounded-xl ${bg}`}>
            <Icon className={`h-5 w-5 ${color}`} />
          </div>
          {trend && (
            <div
              className={`flex items-center gap-1 text-xs font-medium ${
                trend.value >= 0 ? "text-emerald-500" : "text-red-500"
              }`}
            >
              {trend.value >= 0 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {Math.abs(trend.value)}%
            </div>
          )}
        </div>
        <div className="mt-4">
          <div className="text-2xl font-bold">{value}</div>
          <div className="text-sm font-medium text-foreground mt-0.5">{title}</div>
          <div className="text-xs text-muted-foreground mt-1">{subtitle}</div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Custom Tooltip ───────────────────────────────────────────────────────────

function CustomTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="font-semibold mb-2">{label}</p>
        {payload.map((p) => (
          <div key={p.name} className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full" style={{ background: p.color }} />
            <span className="text-muted-foreground">{p.name}:</span>
            <span className="font-medium">{p.value.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

const RISK_COLORS = {
  heart: "#ef4444",
  diabetes: "#f59e0b",
  kidney: "#3b82f6",
};

const PIE_COLORS = ["#3b82f6", "#f59e0b", "#ef4444", "#10b981", "#8b5cf6"];

// ─── Dashboard Page ───────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user } = useUser();
  const { data: historyData, isLoading } = useHistory({ skip: 0, limit: 20 });

  const firstName = user?.firstName || user?.username || "there";
  const predictions = historyData?.items || [];
  const recent5 = predictions.slice(0, 5);

  // Compute derived stats
  const totalPredictions = historyData?.total || 0;
  const avgHeart = predictions.length
    ? predictions.reduce((s, p) => s + p.heart_risk, 0) / predictions.length
    : 0;
  const avgDiabetes = predictions.length
    ? predictions.reduce((s, p) => s + p.diabetes_risk, 0) / predictions.length
    : 0;
  const avgKidney = predictions.length
    ? predictions.reduce((s, p) => s + p.kidney_risk, 0) / predictions.length
    : 0;

  // Chart data for risk trends (last 10)
  const trendData = [...predictions]
    .reverse()
    .slice(-10)
    .map((p, i) => ({
      name: `#${i + 1}`,
      Heart: p.heart_risk,
      Diabetes: p.diabetes_risk,
      Kidney: p.kidney_risk,
    }));

  // Health condition distribution (from most recent)
  const latestConditions = predictions[0]?.health_condition
    ? Object.entries(predictions[0].health_condition)
        .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(1)) }))
        .sort((a, b) => b.value - a.value)
    : [];

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Good day, {firstName} 👋
          </h1>
          <p className="text-muted-foreground mt-1">
            {totalPredictions > 0
              ? `You have ${totalPredictions} prediction${totalPredictions !== 1 ? "s" : ""} on record.`
              : "Run your first disease risk prediction to get started."}
          </p>
        </div>
        <Link href="/predictions/new">
          <Button size="lg" className="group">
            <PlusCircle className="h-5 w-5" />
            New Prediction
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </Button>
        </Link>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { href: "/predictions/new", icon: PlusCircle, label: "New Prediction", color: "text-blue-600", bg: "bg-blue-600/10" },
          { href: "/upload", icon: Upload, label: "Upload PDF", color: "text-emerald-600", bg: "bg-emerald-600/10" },
          { href: "/history", icon: History, label: "View History", color: "text-purple-600", bg: "bg-purple-600/10" },
          { href: "/profile", icon: Activity, label: "Health Profile", color: "text-amber-600", bg: "bg-amber-600/10" },
        ].map((action) => (
          <Link key={action.href} href={action.href}>
            <Card className="card-hover cursor-pointer h-full">
              <CardContent className="flex flex-col items-center gap-3 p-5 text-center">
                <div className={`h-10 w-10 rounded-xl ${action.bg} flex items-center justify-center`}>
                  <action.icon className={`h-5 w-5 ${action.color}`} />
                </div>
                <span className="text-sm font-medium">{action.label}</span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Stats */}
      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={Activity}
            title="Total Predictions"
            value={totalPredictions}
            subtitle="All time"
            color="text-blue-600"
            bg="bg-blue-600/10"
          />
          <StatCard
            icon={Heart}
            title="Avg Heart Risk"
            value={`${avgHeart.toFixed(1)}%`}
            subtitle="Across all predictions"
            color="text-red-500"
            bg="bg-red-500/10"
          />
          <StatCard
            icon={Brain}
            title="Avg Diabetes Risk"
            value={`${avgDiabetes.toFixed(1)}%`}
            subtitle="Across all predictions"
            color="text-amber-500"
            bg="bg-amber-500/10"
          />
          <StatCard
            icon={Activity}
            title="Avg Kidney Risk"
            value={`${avgKidney.toFixed(1)}%`}
            subtitle="Across all predictions"
            color="text-blue-500"
            bg="bg-blue-500/10"
          />
        </div>
      )}

      {/* Charts Row */}
      {totalPredictions > 0 && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Risk Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Risk Score Trends</CardTitle>
              <CardDescription>Your last {Math.min(10, predictions.length)} predictions</CardDescription>
            </CardHeader>
            <CardContent>
              {trendData.length < 2 ? (
                <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">
                  Run more predictions to see trends
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={trendData}>
                    <defs>
                      {Object.entries(RISK_COLORS).map(([key, color]) => (
                        <linearGradient key={key} id={`gradient-${key}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={color} stopOpacity={0.15} />
                          <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                      ))}
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} className="text-muted-foreground" />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} className="text-muted-foreground" />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="Heart" stroke={RISK_COLORS.heart} fill={`url(#gradient-heart)`} strokeWidth={2} />
                    <Area type="monotone" dataKey="Diabetes" stroke={RISK_COLORS.diabetes} fill={`url(#gradient-diabetes)`} strokeWidth={2} />
                    <Area type="monotone" dataKey="Kidney" stroke={RISK_COLORS.kidney} fill={`url(#gradient-kidney)`} strokeWidth={2} />
                    <Legend />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          {/* Health Condition Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Health Condition Distribution</CardTitle>
              <CardDescription>
                {predictions[0] ? "From most recent prediction" : "No data yet"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {latestConditions.length === 0 ? (
                <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">
                  Run a prediction to see condition analysis
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={latestConditions}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {latestConditions.map((_, index) => (
                        <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => [`${Number(v).toFixed(1)}%`]} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Predictions */}
      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base">Recent Predictions</CardTitle>
            <CardDescription>Your latest health assessments</CardDescription>
          </div>
          {totalPredictions > 5 && (
            <Link href="/history">
              <Button variant="ghost" size="sm">
                View all <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : recent5.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
                <Activity className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="font-semibold mb-1">No predictions yet</h3>
              <p className="text-muted-foreground text-sm mb-6 max-w-xs">
                Start your first disease risk assessment to see your results here.
              </p>
              <Link href="/predictions/new">
                <Button>
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Run First Prediction
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recent5.map((prediction) => {
                const composite = getCompositeScore(
                  prediction.heart_risk,
                  prediction.diabetes_risk,
                  prediction.kidney_risk
                );
                const level = getRiskLevel(composite);
                return (
                  <Link
                    key={prediction.id}
                    href={`/history/${prediction.id}`}
                    className="flex items-center gap-4 p-4 rounded-xl border border-border/50 hover:border-blue-200 hover:bg-muted/30 transition-all group"
                  >
                    <div className="h-10 w-10 rounded-xl bg-blue-600/10 flex items-center justify-center shrink-0">
                      <Activity className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={level as "low" | "moderate" | "high" | "critical"} className="text-[10px]">
                          {getRiskLabel(level)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(prediction.created_at)}
                        </span>
                      </div>
                      <div className="flex gap-4 text-sm">
                        <span className="text-red-500">♥ {prediction.heart_risk.toFixed(0)}%</span>
                        <span className="text-amber-500">⬡ {prediction.diabetes_risk.toFixed(0)}%</span>
                        <span className="text-blue-500">⊕ {prediction.kidney_risk.toFixed(0)}%</span>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-blue-600 group-hover:translate-x-1 transition-all shrink-0" />
                  </Link>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
