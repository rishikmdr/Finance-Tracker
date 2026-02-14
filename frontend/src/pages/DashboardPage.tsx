import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { TrendingUp, TrendingDown, Wallet, Coins } from 'lucide-react';
import api from '../lib/api';
import type { DashboardSummary } from '../types/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

function formatINR(value: number): string {
  if (value >= 10000000) return `${(value / 10000000).toFixed(2)} Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(2)} L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)} K`;
  return value.toFixed(0);
}

export function DashboardPage() {
  const { data, isLoading, error } = useQuery<DashboardSummary>({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/dashboard/summary').then((r) => r.data),
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

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

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

        {/* Asset Breakdown */}
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

      {/* AI Console placeholder */}
      <div className="rounded-xl border border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50 p-6">
        <h2 className="text-lg font-semibold text-gray-900">AI Portfolio Insights</h2>
        <p className="mt-2 text-sm text-gray-500">
          AI-powered portfolio analysis will appear here once you add your holdings and connect your
          Anthropic API key. The AI will analyze your portfolio health, identify risks, and suggest
          next steps.
        </p>
      </div>
    </div>
  );
}
