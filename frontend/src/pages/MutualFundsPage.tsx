import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Pause, Play } from 'lucide-react';
import api from '../lib/api';
import type { MFHolding, SIP } from '../types/api';

export function MutualFundsPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<'holdings' | 'sips'>('holdings');
  const [showMFForm, setShowMFForm] = useState(false);
  const [showSIPForm, setShowSIPForm] = useState(false);

  const { data: holdings = [] } = useQuery<MFHolding[]>({
    queryKey: ['mf-holdings'],
    queryFn: () => api.get('/holdings/mf').then((r) => r.data),
  });

  const { data: sips = [] } = useQuery<SIP[]>({
    queryKey: ['sips'],
    queryFn: () => api.get('/holdings/sips?active_only=false').then((r) => r.data),
  });

  const createMF = useMutation({
    mutationFn: (data: any) => api.post('/holdings/mf', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] });
      setShowMFForm(false);
    },
  });

  const createSIP = useMutation({
    mutationFn: (data: any) => api.post('/holdings/sips', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sips'] });
      setShowSIPForm(false);
    },
  });

  const toggleSIP = useMutation({
    mutationFn: (id: number) => api.put(`/holdings/sips/${id}/pause`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sips'] }),
  });

  const deleteMF = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/mf/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['mf-holdings'] }),
  });

  const deleteSIP = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/sips/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sips'] }),
  });

  const totalMFInvested = holdings.reduce((sum, h) => sum + h.units * h.avg_nav, 0);
  const totalSIPMonthly = sips.filter((s) => s.is_active).reduce((sum, s) => sum + s.amount, 0);

  const handleMFSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    createMF.mutate({
      scheme_code: fd.get('scheme_code'),
      scheme_name: fd.get('scheme_name'),
      category: fd.get('category') || null,
      units: Number(fd.get('units')),
      avg_nav: Number(fd.get('avg_nav')),
      investment_mode: fd.get('investment_mode'),
      buy_date: fd.get('buy_date'),
      folio_number: fd.get('folio_number') || null,
      platform: fd.get('platform') || null,
    });
  };

  const handleSIPSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    createSIP.mutate({
      scheme_code: fd.get('scheme_code'),
      scheme_name: fd.get('scheme_name'),
      amount: Number(fd.get('amount')),
      day_of_month: Number(fd.get('day_of_month')),
      frequency: fd.get('frequency'),
      start_date: fd.get('start_date'),
      step_up_percent: fd.get('step_up_percent') ? Number(fd.get('step_up_percent')) : null,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mutual Funds</h1>
          <p className="text-sm text-gray-500">
            {holdings.length} holdings | Invested: {(totalMFInvested / 100000).toFixed(2)}L |
            Monthly SIP: {totalSIPMonthly.toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
        <button
          onClick={() => setTab('holdings')}
          className={`flex-1 rounded-md px-4 py-2 text-sm font-medium ${
            tab === 'holdings' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
          }`}
        >
          Holdings ({holdings.length})
        </button>
        <button
          onClick={() => setTab('sips')}
          className={`flex-1 rounded-md px-4 py-2 text-sm font-medium ${
            tab === 'sips' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
          }`}
        >
          SIPs ({sips.length})
        </button>
      </div>

      {/* Holdings Tab */}
      {tab === 'holdings' && (
        <>
          <button
            onClick={() => setShowMFForm(!showMFForm)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" /> Add MF Holding
          </button>

          {showMFForm && (
            <form onSubmit={handleMFSubmit}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Scheme Code</label>
                  <input name="scheme_code" required placeholder="119551"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Scheme Name</label>
                  <input name="scheme_name" required placeholder="HDFC Flexi Cap Fund"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Category</label>
                  <input name="category" placeholder="Large Cap"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Units</label>
                  <input name="units" type="number" step="0.0001" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Avg NAV</label>
                  <input name="avg_nav" type="number" step="0.0001" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Mode</label>
                  <select name="investment_mode"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    <option value="lumpsum">Lumpsum</option>
                    <option value="sip">SIP</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Buy Date</label>
                  <input name="buy_date" type="date" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Folio</label>
                  <input name="folio_number"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Platform</label>
                  <input name="platform" placeholder="Groww / Kuvera"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={createMF.isPending}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {createMF.isPending ? 'Adding...' : 'Add Holding'}
                </button>
                <button type="button" onClick={() => setShowMFForm(false)}
                  className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-600">
                  Cancel
                </button>
              </div>
            </form>
          )}

          {holdings.length === 0 ? (
            <div className="rounded-xl border border-gray-200 bg-white p-10 text-center">
              <p className="text-gray-400">No mutual fund holdings yet.</p>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-gray-100 bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 font-medium text-gray-500">Scheme</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Category</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Units</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Avg NAV</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Invested</th>
                    <th className="px-4 py-3 font-medium text-gray-500">Mode</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {holdings.map((h) => (
                    <tr key={h.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-900">{h.scheme_name}</div>
                        <div className="text-xs text-gray-400">{h.scheme_code}</div>
                      </td>
                      <td className="px-4 py-3 text-gray-500">{h.category || '-'}</td>
                      <td className="px-4 py-3">{Number(h.units).toFixed(3)}</td>
                      <td className="px-4 py-3">{Number(h.avg_nav).toFixed(2)}</td>
                      <td className="px-4 py-3 font-medium">
                        {(h.units * h.avg_nav).toFixed(0)}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          h.investment_mode === 'sip'
                            ? 'bg-green-50 text-green-700'
                            : 'bg-blue-50 text-blue-700'
                        }`}>
                          {h.investment_mode}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <button onClick={() => deleteMF.mutate(h.id)}
                          className="text-gray-400 hover:text-red-500">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* SIPs Tab */}
      {tab === 'sips' && (
        <>
          <button
            onClick={() => setShowSIPForm(!showSIPForm)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" /> Add SIP
          </button>

          {showSIPForm && (
            <form onSubmit={handleSIPSubmit}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Scheme Code</label>
                  <input name="scheme_code" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Scheme Name</label>
                  <input name="scheme_name" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Amount</label>
                  <input name="amount" type="number" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Day of Month</label>
                  <input name="day_of_month" type="number" min="1" max="28" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Frequency</label>
                  <select name="frequency"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input name="start_date" type="date" required
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Step-up %/yr</label>
                  <input name="step_up_percent" type="number" step="0.01" placeholder="10"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                </div>
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={createSIP.isPending}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                  {createSIP.isPending ? 'Adding...' : 'Add SIP'}
                </button>
                <button type="button" onClick={() => setShowSIPForm(false)}
                  className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-600">
                  Cancel
                </button>
              </div>
            </form>
          )}

          {sips.length === 0 ? (
            <div className="rounded-xl border border-gray-200 bg-white p-10 text-center">
              <p className="text-gray-400">No SIPs yet. Add your first SIP above.</p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {sips.map((sip) => (
                <div key={sip.id}
                  className="rounded-xl border border-gray-200 bg-white p-5 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{sip.scheme_name}</h3>
                      <p className="text-xs text-gray-400">{sip.scheme_code}</p>
                    </div>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      sip.is_active
                        ? 'bg-green-50 text-green-700'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {sip.is_active ? 'Active' : 'Paused'}
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {Number(sip.amount).toLocaleString('en-IN')}
                    <span className="text-sm font-normal text-gray-400">/{sip.frequency}</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    Every {sip.day_of_month}th | Since {sip.start_date}
                    {sip.step_up_percent && ` | Step-up: ${sip.step_up_percent}%/yr`}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => toggleSIP.mutate(sip.id)}
                      className="flex items-center gap-1 rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-200">
                      {sip.is_active ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                      {sip.is_active ? 'Pause' : 'Resume'}
                    </button>
                    <button onClick={() => deleteSIP.mutate(sip.id)}
                      className="flex items-center gap-1 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-100">
                      <Trash2 className="h-3 w-3" /> Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
