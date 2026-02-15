import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell, LineChart, Line, Area, AreaChart,
} from 'recharts';
import {
  TrendingUp, TrendingDown, IndianRupee, Target, BarChart3, RefreshCw,
} from 'lucide-react';
import api from '../lib/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

function formatINR(value: number): string {
  if (value >= 10000000) return `${(value / 10000000).toFixed(2)} Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(2)} L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)} K`;
  return value.toFixed(0);
}

export function AnalyticsPage() {
  const { data: netWorth, isLoading: nwLoading, refetch: refetchNW } = useQuery({
    queryKey: ['net-worth'],
    queryFn: () => api.get('/portfolio/net-worth').then((r) => r.data),
  });

  const { data: trends } = useQuery({
    queryKey: ['trends'],
    queryFn: () => api.get('/portfolio/trends?months=12').then((r) => r.data),
  });

  const { data: expenseBreakdown } = useQuery({
    queryKey: ['expense-breakdown'],
    queryFn: () => api.get('/portfolio/expense-breakdown').then((r) => r.data),
  });

  const refreshPrices = async () => {
    await api.post('/prices/refresh');
    refetchNW();
  };

  if (nwLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  const allocationData = netWorth?.allocation
    ? Object.entries(netWorth.allocation).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value: value as number,
      }))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio Analytics</h1>
          <p className="text-sm text-gray-500">Deep dive into your financial performance</p>
        </div>
        <button
          onClick={refreshPrices}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Prices
        </button>
      </div>

      {/* Net Worth Summary Cards */}
      {netWorth && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">Net Worth</span>
              <IndianRupee className="h-5 w-5 text-blue-500" />
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{formatINR(netWorth.net_worth)}</p>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">Total Invested</span>
              <Target className="h-5 w-5 text-purple-500" />
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{formatINR(netWorth.total_invested)}</p>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">Total P&L</span>
              {netWorth.total_pnl >= 0 ? (
                <TrendingUp className="h-5 w-5 text-green-500" />
              ) : (
                <TrendingDown className="h-5 w-5 text-red-500" />
              )}
            </div>
            <p className={`mt-2 text-2xl font-bold ${netWorth.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {netWorth.total_pnl >= 0 ? '+' : ''}{formatINR(netWorth.total_pnl)}
            </p>
            <p className={`text-sm ${netWorth.total_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {netWorth.total_pnl_pct >= 0 ? '+' : ''}{netWorth.total_pnl_pct}%
            </p>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-500">Liabilities</span>
              <BarChart3 className="h-5 w-5 text-red-500" />
            </div>
            <p className="mt-2 text-2xl font-bold text-red-600">{formatINR(netWorth.total_liabilities)}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Asset Allocation Pie */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h2>
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
            <p className="text-sm text-gray-400 py-10 text-center">Add holdings to see allocation</p>
          )}
        </div>

        {/* Income vs Expense Trend */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Income vs Expenses (12M)</h2>
          {trends && trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatINR(v)} />
                <Tooltip formatter={(v: number) => `₹${v.toLocaleString('en-IN')}`} />
                <Legend />
                <Bar dataKey="income" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expenses" name="Expenses" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 py-10 text-center">Add income & expenses to see trends</p>
          )}
        </div>

        {/* Savings Trend */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Savings Trend</h2>
          {trends && trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatINR(v)} />
                <Tooltip formatter={(v: number) => `₹${v.toLocaleString('en-IN')}`} />
                <Area
                  type="monotone"
                  dataKey="savings"
                  stroke="#3b82f6"
                  fill="#3b82f680"
                  name="Savings"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 py-10 text-center">No data yet</p>
          )}
        </div>

        {/* Expense Breakdown */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Expense Breakdown (This Month)</h2>
          {expenseBreakdown && expenseBreakdown.length > 0 ? (
            <div className="space-y-3">
              {expenseBreakdown.map((cat: any, i: number) => (
                <div key={cat.category} className="flex items-center gap-3">
                  <div
                    className="h-3 w-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-700 truncate">{cat.category}</span>
                      <span className="font-medium text-gray-900 ml-2">₹{cat.amount.toLocaleString('en-IN')}</span>
                    </div>
                    <div className="mt-1 h-1.5 rounded-full bg-gray-100">
                      <div
                        className="h-1.5 rounded-full"
                        style={{
                          width: `${cat.percentage}%`,
                          backgroundColor: COLORS[i % COLORS.length],
                        }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 w-10 text-right">{cat.percentage}%</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 py-10 text-center">No expenses this month</p>
          )}
        </div>
      </div>

      {/* Stock & MF Returns Tables */}
      {netWorth?.stocks && netWorth.stocks.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Stock Returns</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500">
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium text-right">Qty</th>
                  <th className="pb-3 font-medium text-right">Avg Price</th>
                  <th className="pb-3 font-medium text-right">CMP</th>
                  <th className="pb-3 font-medium text-right">Invested</th>
                  <th className="pb-3 font-medium text-right">Current</th>
                  <th className="pb-3 font-medium text-right">P&L</th>
                  <th className="pb-3 font-medium text-right">P&L %</th>
                  <th className="pb-3 font-medium text-right">XIRR</th>
                  <th className="pb-3 font-medium text-right">Day %</th>
                </tr>
              </thead>
              <tbody>
                {netWorth.stocks.map((s: any) => (
                  <tr key={s.id} className="border-b border-gray-50">
                    <td className="py-3 font-medium text-gray-900">{s.symbol}</td>
                    <td className="py-3">
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs capitalize">{s.investment_type}</span>
                    </td>
                    <td className="py-3 text-right">{s.quantity}</td>
                    <td className="py-3 text-right">₹{s.avg_buy_price.toLocaleString('en-IN')}</td>
                    <td className="py-3 text-right">{s.current_price ? `₹${s.current_price.toLocaleString('en-IN')}` : '—'}</td>
                    <td className="py-3 text-right">₹{s.invested.toLocaleString('en-IN')}</td>
                    <td className="py-3 text-right">{s.current_value ? `₹${s.current_value.toLocaleString('en-IN')}` : '—'}</td>
                    <td className={`py-3 text-right font-medium ${s.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {s.pnl != null ? `${s.pnl >= 0 ? '+' : ''}₹${Math.abs(s.pnl).toLocaleString('en-IN')}` : '—'}
                    </td>
                    <td className={`py-3 text-right ${s.pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {s.pnl_pct != null ? `${s.pnl_pct >= 0 ? '+' : ''}${s.pnl_pct}%` : '—'}
                    </td>
                    <td className={`py-3 text-right ${(s.xirr || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {s.xirr != null ? `${s.xirr}%` : '—'}
                    </td>
                    <td className={`py-3 text-right ${(s.day_change_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {s.day_change_pct != null ? `${s.day_change_pct >= 0 ? '+' : ''}${s.day_change_pct}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {netWorth?.mutual_funds && netWorth.mutual_funds.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Mutual Fund Returns</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500">
                  <th className="pb-3 font-medium">Scheme</th>
                  <th className="pb-3 font-medium">Category</th>
                  <th className="pb-3 font-medium text-right">Units</th>
                  <th className="pb-3 font-medium text-right">Avg NAV</th>
                  <th className="pb-3 font-medium text-right">Current NAV</th>
                  <th className="pb-3 font-medium text-right">Invested</th>
                  <th className="pb-3 font-medium text-right">Current</th>
                  <th className="pb-3 font-medium text-right">P&L</th>
                  <th className="pb-3 font-medium text-right">XIRR</th>
                </tr>
              </thead>
              <tbody>
                {netWorth.mutual_funds.map((m: any) => (
                  <tr key={m.id} className="border-b border-gray-50">
                    <td className="py-3 font-medium text-gray-900 max-w-[200px] truncate">{m.scheme_name}</td>
                    <td className="py-3 text-gray-500">{m.category || '—'}</td>
                    <td className="py-3 text-right">{m.units.toFixed(3)}</td>
                    <td className="py-3 text-right">₹{m.avg_nav.toFixed(2)}</td>
                    <td className="py-3 text-right">{m.current_nav ? `₹${m.current_nav.toFixed(2)}` : '—'}</td>
                    <td className="py-3 text-right">₹{m.invested.toLocaleString('en-IN')}</td>
                    <td className="py-3 text-right">{m.current_value ? `₹${m.current_value.toLocaleString('en-IN')}` : '—'}</td>
                    <td className={`py-3 text-right font-medium ${(m.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {m.pnl != null ? `${m.pnl >= 0 ? '+' : ''}₹${Math.abs(m.pnl).toLocaleString('en-IN')}` : '—'}
                    </td>
                    <td className={`py-3 text-right ${(m.xirr || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {m.xirr != null ? `${m.xirr}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
