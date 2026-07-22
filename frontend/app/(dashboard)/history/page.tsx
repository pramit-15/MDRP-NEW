"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  History as HistoryIcon, Search, Trash2, Eye, Calendar,
  ChevronLeft, ChevronRight, Filter, SortAsc, SortDesc,
  Activity, ArrowRight, LayoutList, LayoutGrid, AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogFooter,
} from "@/components/ui/dialog";
import { useHistory, useDeleteHistory } from "@/hooks/use-predictions";
import { formatDate, formatRelativeTime, getCompositeScore } from "@/lib/utils";
import { getRiskLevel, getRiskLabel, getRiskBgColor } from "@/types";
import type { HistoryItem } from "@/types";

const PAGE_SIZE = 10;

function RiskBadges({ item }: { item: HistoryItem }) {
  return (
    <div className="flex gap-2 flex-wrap">
      <span className="text-xs font-medium text-red-500">♥ {item.heart_risk.toFixed(0)}%</span>
      <span className="text-xs font-medium text-amber-500">⬡ {item.diabetes_risk.toFixed(0)}%</span>
      <span className="text-xs font-medium text-blue-500">⊕ {item.kidney_risk.toFixed(0)}%</span>
    </div>
  );
}

function DeleteDialog({
  open,
  onConfirm,
  onCancel,
  isDeleting,
}: {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting: boolean;
}) {
  return (
    <Dialog open={open} onOpenChange={(o) => !o && onCancel()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Prediction</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete this prediction? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={onConfirm} loading={isDeleting}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function HistoryPage() {
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [view, setView] = useState<"table" | "grid">("table");
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data, isLoading } = useHistory({ skip: page * PAGE_SIZE, limit: PAGE_SIZE });
  const { mutate: deleteHistory, isPending: isDeleting } = useDeleteHistory();

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  // Client-side search filter (on current page)
  const filtered = items.filter((item) => {
    if (!search) return true;
    const s = search.toLowerCase();
    const composite = getCompositeScore(item.heart_risk, item.diabetes_risk, item.kidney_risk);
    const level = getRiskLevel(composite);
    return (
      level.includes(s) ||
      item.heart_risk.toString().includes(s) ||
      item.diabetes_risk.toString().includes(s)
    );
  });

  const sorted = [...filtered].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();
    return sortDir === "desc" ? dateB - dateA : dateA - dateB;
  });

  const handleDelete = () => {
    if (deleteId) {
      deleteHistory(deleteId, { onSuccess: () => setDeleteId(null) });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <HistoryIcon className="h-6 w-6 text-blue-600" />
            Prediction History
          </h1>
          <p className="text-muted-foreground mt-1">
            {total} total prediction{total !== 1 ? "s" : ""}
          </p>
        </div>
        <Link href="/predictions/new">
          <Button>
            <Activity className="h-4 w-4 mr-2" />
            New Prediction
          </Button>
        </Link>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by risk level..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setSortDir((d) => (d === "desc" ? "asc" : "desc"))}
            title={`Sort ${sortDir === "desc" ? "oldest first" : "newest first"}`}
          >
            {sortDir === "desc" ? <SortDesc className="h-4 w-4" /> : <SortAsc className="h-4 w-4" />}
          </Button>
          <Button
            variant={view === "table" ? "default" : "outline"}
            size="icon"
            onClick={() => setView("table")}
          >
            <LayoutList className="h-4 w-4" />
          </Button>
          <Button
            variant={view === "grid" ? "default" : "outline"}
            size="icon"
            onClick={() => setView("grid")}
          >
            <LayoutGrid className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      ) : sorted.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-20 text-center">
            <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center mb-4">
              <HistoryIcon className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-1">
              {search ? "No matching predictions" : "No predictions yet"}
            </h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-xs">
              {search
                ? "Try a different search term."
                : "Run your first disease risk assessment to see your history here."}
            </p>
            {!search && (
              <Link href="/predictions/new">
                <Button>Run First Prediction</Button>
              </Link>
            )}
          </CardContent>
        </Card>
      ) : view === "grid" ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {sorted.map((item, i) => {
              const composite = getCompositeScore(item.heart_risk, item.diabetes_risk, item.kidney_risk);
              const level = getRiskLevel(composite);
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Card className="card-hover group">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between mb-4">
                        <Badge className={getRiskBgColor(level)}>{getRiskLabel(level)}</Badge>
                        <button
                          onClick={() => setDeleteId(item.id)}
                          className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-500 transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="text-2xl font-bold mb-1">{composite.toFixed(1)}%</div>
                      <RiskBadges item={item} />
                      <div className="flex items-center justify-between mt-4 pt-3 border-t border-border/50">
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatRelativeTime(item.created_at)}
                        </span>
                        <Link href={`/history/${item.id}`}>
                          <Button variant="ghost" size="sm" className="h-7 text-xs">
                            View <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      ) : (
        <Card>
          <div className="divide-y divide-border/50">
            {sorted.map((item, i) => {
              const composite = getCompositeScore(item.heart_risk, item.diabetes_risk, item.kidney_risk);
              const level = getRiskLevel(composite);
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.03 }}
                  className="flex items-center gap-4 px-6 py-4 hover:bg-muted/30 transition-colors group"
                >
                  <div className="h-9 w-9 rounded-xl bg-blue-600/10 flex items-center justify-center shrink-0">
                    <Activity className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <Badge className={`${getRiskBgColor(level)} text-[10px]`}>
                        {getRiskLabel(level)}
                      </Badge>
                      <span className="text-sm font-bold">{composite.toFixed(1)}%</span>
                    </div>
                    <RiskBadges item={item} />
                  </div>
                  <div className="hidden sm:block text-xs text-muted-foreground flex items-center gap-1">
                    <Calendar className="h-3 w-3 mr-1" />
                    {formatDate(item.created_at)}
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Link href={`/history/${item.id}`}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-red-500"
                      onClick={() => setDeleteId(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            Page {page + 1} of {totalPages} ({total} total)
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      <DeleteDialog
        open={!!deleteId}
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
        isDeleting={isDeleting}
      />
    </div>
  );
}
