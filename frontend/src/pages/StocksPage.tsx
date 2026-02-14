import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2 } from 'lucide-react';
import api from '../lib/api';
import type { StockHolding } from '../types/api';

const INVESTMENT_TYPES = [
  { value: 'long_term', label: 'Long Term' },
  { value: 'swing', label: 'Swing Trade' },
  { value: 'positional', label: 'Positional' },
  { value: 'ipo', label: 'IPO' },
];

export function StocksPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [filterType, setFilterType] = useState<string>('');

  const { data: stocks = [], isLoading } = useQuery<StockHolding[]>({
    queryKey: ['stocks', filterType],
    queryFn: () =>
      api
        .get('/holdings/stocks', { params: filterType ? { investment_type: filterType } : {} })
        .then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/stocks/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['stocks'] }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/holdings/stocks', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stocks'] });
      setShowForm(false);
    },
  });

  const handleCreate = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    createMutation.mutate({
      symbol: fd.get('symbol'),
      exchange: fd.get('exchange'),
      investment_type: fd.get('investment_type'),
      quantity: Number(fd.get('quantity')),
      avg_buy_price: Number(fd.get('avg_buy_price')),
      buy_date: fd.get('buy_date'),
      broker: fd.get('broker') || null,
    });
  };

  const totalInvested = stocks.reduce((sum, s) => sum + s.quantity * s.avg_buy_price, 0);

  // Group by investment type
  const grouped = stocks.reduce(
    (acc, s) => {
      const key = s.investment_type;
      if (!acc[key]) acc[key] = [];
      acc[key].push(s);
      return acc;
    },
    {} as Record<string, StockHolding[]>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stocks</h1>
          <p className="text-sm text-gray-500">
            {stocks.length} holdings | Invested: {(totalInvested / 100000).toFixed(2)}L
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          Add Stock
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilterType('')}
          className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
            !filterType ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
          }`}
        >
          All
        </button>
        {INVESTMENT_TYPES.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setFilterType(value)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
              filterType === value ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Add stock form */}
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="rounded-xl border border-gray-200 bg-white p-6 space-y-4"
        >
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Symbol</label>
              <input name="symbol" required placeholder="RELIANCE"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Exchange</label>
              <select name="exchange"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                <option value="NSE">NSE</option>
                <option value="BSE">BSE</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Type</label>
              <select name="investment_type"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                {INVESTMENT_TYPES.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Quantity</label>
              <input name="quantity" type="number" step="0.0001" required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Avg Buy Price</label>
              <input name="avg_buy_price" type="number" step="0.01" required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Buy Date</label>
              <input name="buy_date" type="date" required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Broker</label>
              <input name="broker" placeholder="Zerodha"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={createMutation.isPending}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
              {createMutation.isPending ? 'Adding...' : 'Add Stock'}
            </button>
            <button type="button" onClick={() => setShowForm(false)}
              className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-600">
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Stock table */}
      {isLoading ? (
        <div className="flex justify-center py-10">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      ) : stocks.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-10 text-center">
          <p className="text-gray-400">No stock holdings yet. Add your first stock above.</p>
        </div>
      ) : (
        Object.entries(grouped).map(([type, holdings]) => (
          <div key={type}>
            <h3 className="mb-2 text-sm font-semibold uppercase text-gray-400">
              {type.replace('_', ' ')}
            </h3>
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-gray-100 bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 font-medium text-gray-500">Symbol</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Qty</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Avg Price</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Invested</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Buy Date</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Broker</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {holdings.map((stock) => (
                    <tr key={stock.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {stock.symbol}
                        <span className="ml-1 text-xs text-gray-400">{stock.exchange}</span>
                      </td>
                      <td className="px-4 py-3">{stock.quantity}</td>
                      <td className="px-4 py-3">{Number(stock.avg_buy_price).toFixed(2)}</td>
                      <td className="px-4 py-3 font-medium">
                        {(stock.quantity * stock.avg_buy_price).toFixed(0)}
                      </td>
                      <td className="px-4 py-3 text-gray-500">{stock.buy_date}</td>
                      <td className="px-4 py-3 text-gray-500">{stock.broker || '-'}</td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => deleteMutation.mutate(stock.id)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
