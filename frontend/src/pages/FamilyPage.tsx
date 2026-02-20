import { useQuery } from '@tanstack/react-query';
import { Users, TrendingUp, Wallet, ArrowDownUp } from 'lucide-react';
import api from '../lib/api';

function formatINR(value: number): string {
  if (value >= 10000000) return `${(value / 10000000).toFixed(2)} Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(2)} L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)} K`;
  return value.toFixed(0);
}

interface FamilySummary {
  family_name: string;
  net_worth: number;
  total_assets: number;
  total_liabilities: number;
  asset_breakdown: Record<string, number>;
  month_summary: { income: number; expenses: number; savings: number };
  members: { id: number; name: string; total_assets: number }[];
}

export function FamilyPage() {
  const { data, isLoading, error } = useQuery<FamilySummary>({
    queryKey: ['family-summary'],
    queryFn: () => api.get('/dashboard/family-summary').then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-center">
        <Users className="h-10 w-10 text-amber-400 mx-auto mb-3" />
        <h2 className="text-lg font-semibold text-gray-900">No Family Setup</h2>
        <p className="mt-2 text-sm text-gray-500">
          Create a family in Settings to see combined family finances here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Users className="h-7 w-7 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{data.family_name}</h1>
          <p className="text-sm text-gray-500">Combined family financial overview</p>
        </div>
      </div>

      {/* Family totals */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Family Net Worth</span>
            <Wallet className="h-5 w-5 text-blue-500" />
          </div>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatINR(data.net_worth)}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Total Assets</span>
            <TrendingUp className="h-5 w-5 text-green-500" />
          </div>
          <p className="mt-2 text-2xl font-bold text-green-600">{formatINR(data.total_assets)}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Monthly Savings</span>
            <ArrowDownUp className="h-5 w-5 text-purple-500" />
          </div>
          <p className={`mt-2 text-2xl font-bold ${data.month_summary.savings >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatINR(data.month_summary.savings)}
          </p>
        </div>
      </div>

      {/* Members */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Family Members</h2>
        <div className="space-y-3">
          {data.members.map((member) => {
            const share = data.total_assets > 0 ? (member.total_assets / data.total_assets) * 100 : 0;
            return (
              <div key={member.id} className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
                  {member.name.charAt(0)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-900">{member.name}</span>
                    <span className="text-sm font-semibold text-gray-700">{formatINR(member.total_assets)}</span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-gray-100">
                    <div
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${share}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400">{share.toFixed(1)}% of family assets</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Asset breakdown */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Combined Asset Breakdown</h2>
        <div className="space-y-3">
          {Object.entries(data.asset_breakdown).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm capitalize text-gray-600">{key.replace('_', ' ')}</span>
              <span className="text-sm font-semibold text-gray-900">{formatINR(value)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
