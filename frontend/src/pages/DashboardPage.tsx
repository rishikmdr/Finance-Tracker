import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import {
  TrendingUp, TrendingDown, Wallet, Coins, Brain, RefreshCw,
  AlertTriangle, CheckCircle, Lightbulb, Shield, ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import type { DashboardSummary } from '../types/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

function formatINR(value: number): string {
  if (value >= 10000000) return `${(value / 10000000).toFixed(2)} Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(2)} L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)} K`;
  return value.toFixed(0);
}

interface AIAnalysis {
  health_score: number | null;
  good: string[];
  bad: string[];
  alerts: string[];
  suggestions: string[];
  error: string | null;
}

export function DashboardPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<DashboardSummary>({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/dashboard/summary').then((r) => r.data),
  });

  const { data: analysis, isLoading: aiLoading, refetch: refetchAI } = useQuery<AIAnalysis>({
    queryKey: ['portfolio-analysis'],
    queryFn: () => api.get('/portfolio/analysis').then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });

  const refreshPrices = useMutation({
    mutationFn: () => api.post('/prices/refresh'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['net-worth'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return <div className="text-red-600">Failed to load dashboard</div>;
  }

  const allocationData = data.asset_allocation_pct
    ? Object.entries(data.asset_allocation_pct).map(([key, value]) => ({
        name: key.replace('_', ' '),
        value: Number(value.toFixed(1)),
      }))
    : [];

  const statCards = [
    {
      label: 'Net Worth',
      value: formatINR(data.net_worth),
      icon: Wallet,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      label: 'Total Assets',
      value: formatINR(data.total_assets),
      icon: TrendingUp,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      label: 'Total Liabilities',
      value: formatINR(data.total_liabilities),
      icon: TrendingDown,
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
    {
      label: 'Monthly Savings',
      value: formatINR(data.month_summary.savings),
      icon: Coins,
      color: data.month_summary.savings >= 0 ? 'text-green-600' : 'text-red-600',
      bg: data.month_summary.savings >= 0 ? 'bg-green-50' : 'bg-red-50',
    },
  ];

  const healthColor = (score: number) => {
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const healthBg = (score: number) => {
    if (score >= 75) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={() => refreshPrices.mutate()}
          disabled={refreshPrices.isPending}
          className="flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
        >
          <RefreshCw className={`h-4 w-4 ${refreshPrices.isPending ? 'animate-spin' : ''}`} />
          Refresh Prices
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">{label}</span>
              <div className={`rounded-lg ${bg} p-2`}>
                <Icon className={`h-5 w-5 ${color}`} />
              </div>
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Asset Allocation Pie */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">Asset Allocation</h2>
          {allocationData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, value }) => `${name} ${value}%`}
                >
                  {allocationData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => `${v}%`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="mt-4 text-sm text-gray-400">Add holdings to see allocation</p>
          )}
        </div>

        {/* Asset Breakdown + Monthly Summary */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">Asset Breakdown</h2>
          <div className="mt-4 space-y-3">
            {Object.entries(data.asset_breakdown).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm capitalize text-gray-600">
                  {key.replace('_', ' ')}
                </span>
                <span className="text-sm font-semibold text-gray-900">{formatINR(value)}</span>
              </div>
            ))}
          </div>

          <div className="mt-6 border-t border-gray-100 pt-4">
            <h3 className="text-sm font-medium text-gray-500">This Month</h3>
            <div className="mt-2 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Income</span>
                <span className="font-medium text-green-600">
                  {formatINR(data.month_summary.income)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Expenses</span>
                <span className="font-medium text-red-600">
                  {formatINR(data.month_summary.expenses)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Portfolio Insights */}
      <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-100 p-2">
              <Brain className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">AI Portfolio Insights</h2>
              <p className="text-xs text-gray-500">Powered by Claude AI</p>
            </div>
          </div>
          <button
            onClick={() => refetchAI()}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${aiLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {aiLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-6 w-6 animate-spin rounded-full border-3 border-blue-500 border-t-transparent mx-auto" />
              <p className="mt-2 text-sm text-gray-500">Analyzing your portfolio...</p>
            </div>
          </div>
        ) : analysis?.error ? (
          <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              {analysis.error}
            </div>
            {analysis.error.includes('API key') && (
              <Link to="/settings" className="mt-2 inline-flex items-center gap-1 text-blue-600 hover:underline text-xs">
                Go to Settings <ArrowRight className="h-3 w-3" />
              </Link>
            )}
          </div>
        ) : analysis ? (
          <div className="space-y-4">
            {/* Health Score */}
            {analysis.health_score != null && (
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className={`text-3xl font-bold ${healthColor(analysis.health_score)}`}>
                    {analysis.health_score}
                  </div>
                  <div className="text-xs text-gray-500">Health Score</div>
                </div>
                <div className="flex-1">
                  <div className="h-3 rounded-full bg-gray-200">
                    <div
                      className={`h-3 rounded-full transition-all ${healthBg(analysis.health_score)}`}
                      style={{ width: `${analysis.health_score}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {analysis.good.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-green-700 flex items-center gap-1">
                    <CheckCircle className="h-4 w-4" /> What's Good
                  </h3>
                  {analysis.good.map((item, i) => (
                    <p key={i} className="text-sm text-gray-600 pl-5">{item}</p>
                  ))}
                </div>
              )}

              {analysis.bad.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-red-700 flex items-center gap-1">
                    <AlertTriangle className="h-4 w-4" /> Risks
                  </h3>
                  {analysis.bad.map((item, i) => (
                    <p key={i} className="text-sm text-gray-600 pl-5">{item}</p>
                  ))}
                </div>
              )}
            </div>

            {analysis.alerts.length > 0 && (
              <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
                <h3 className="text-sm font-medium text-amber-700 flex items-center gap-1 mb-1">
                  <Shield className="h-4 w-4" /> Alerts
                </h3>
                {analysis.alerts.map((alert, i) => (
                  <p key={i} className="text-sm text-amber-600 pl-5">{alert}</p>
                ))}
              </div>
            )}

            {analysis.suggestions.length > 0 && (
              <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
                <h3 className="text-sm font-medium text-blue-700 flex items-center gap-1 mb-1">
                  <Lightbulb className="h-4 w-4" /> Suggestions
                </h3>
                {analysis.suggestions.map((s, i) => (
                  <p key={i} className="text-sm text-blue-600 pl-5">{s}</p>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500 py-4">
            Add your holdings and AI API key to get personalized insights.
          </p>
        )}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Link
          to="/analytics"
          className="rounded-xl border border-gray-200 bg-white p-4 text-center hover:bg-gray-50 transition-colors"
        >
          <TrendingUp className="h-6 w-6 text-blue-500 mx-auto" />
          <p className="mt-2 text-sm font-medium text-gray-700">Analytics</p>
        </Link>
        <Link
          to="/chat"
          className="rounded-xl border border-gray-200 bg-white p-4 text-center hover:bg-gray-50 transition-colors"
        >
          <Brain className="h-6 w-6 text-purple-500 mx-auto" />
          <p className="mt-2 text-sm font-medium text-gray-700">AI Advisor</p>
        </Link>
        <Link
          to="/expenses"
          className="rounded-xl border border-gray-200 bg-white p-4 text-center hover:bg-gray-50 transition-colors"
        >
          <Coins className="h-6 w-6 text-amber-500 mx-auto" />
          <p className="mt-2 text-sm font-medium text-gray-700">Expenses</p>
        </Link>
        <Link
          to="/settings"
          className="rounded-xl border border-gray-200 bg-white p-4 text-center hover:bg-gray-50 transition-colors"
        >
          <Shield className="h-6 w-6 text-green-500 mx-auto" />
          <p className="mt-2 text-sm font-medium text-gray-700">Settings</p>
        </Link>
      </div>
    </div>
  );
}
