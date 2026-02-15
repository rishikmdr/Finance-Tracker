import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Shield, Briefcase, Bitcoin, Plus, Trash2 } from 'lucide-react';
import api from '../lib/api';

type Tab = 'insurance' | 'esop' | 'crypto';

export function MoreAssetsPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>('insurance');
  const [showForm, setShowForm] = useState(false);

  // Insurance
  const [insForm, setInsForm] = useState({ type: 'term', provider: '', sum_assured: '', annual_premium: '', premium_frequency: 'annual', next_premium_date: '', maturity_date: '', tax_section: '80C', nominees: '' });
  const { data: insurance } = useQuery({ queryKey: ['insurance'], queryFn: () => api.get('/insurance').then(r => r.data) });
  const addInsurance = useMutation({
    mutationFn: () => api.post('/insurance', { ...insForm, sum_assured: parseFloat(insForm.sum_assured), annual_premium: parseFloat(insForm.annual_premium), next_premium_date: insForm.next_premium_date || null, maturity_date: insForm.maturity_date || null }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['insurance'] }); setShowForm(false); },
  });
  const delInsurance = useMutation({ mutationFn: (id: number) => api.delete(`/insurance/${id}`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['insurance'] }) });

  // ESOP
  const [esopForm, setEsopForm] = useState({ company: '', type: 'esop', total_granted: '', vested: '0', exercised: '0', strike_price: '', current_fmv: '', next_vesting_date: '', vesting_schedule: '' });
  const { data: esops } = useQuery({ queryKey: ['esop'], queryFn: () => api.get('/esop').then(r => r.data) });
  const addEsop = useMutation({
    mutationFn: () => api.post('/esop', { ...esopForm, total_granted: parseInt(esopForm.total_granted), vested: parseInt(esopForm.vested || '0'), exercised: parseInt(esopForm.exercised || '0'), strike_price: esopForm.strike_price ? parseFloat(esopForm.strike_price) : null, current_fmv: esopForm.current_fmv ? parseFloat(esopForm.current_fmv) : null, next_vesting_date: esopForm.next_vesting_date || null }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['esop'] }); setShowForm(false); },
  });
  const delEsop = useMutation({ mutationFn: (id: number) => api.delete(`/esop/${id}`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['esop'] }) });

  // Crypto
  const [cryptoForm, setCryptoForm] = useState({ coin: '', quantity: '', avg_buy_price_inr: '', exchange: '' });
  const { data: cryptos } = useQuery({ queryKey: ['crypto'], queryFn: () => api.get('/crypto').then(r => r.data) });
  const addCrypto = useMutation({
    mutationFn: () => api.post('/crypto', { ...cryptoForm, quantity: parseFloat(cryptoForm.quantity), avg_buy_price_inr: parseFloat(cryptoForm.avg_buy_price_inr) }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['crypto'] }); setShowForm(false); },
  });
  const delCrypto = useMutation({ mutationFn: (id: number) => api.delete(`/crypto/${id}`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['crypto'] }) });

  const tabs = [
    { key: 'insurance' as Tab, label: 'Insurance', icon: Shield, count: insurance?.length || 0 },
    { key: 'esop' as Tab, label: 'ESOP/RSU', icon: Briefcase, count: esops?.length || 0 },
    { key: 'crypto' as Tab, label: 'Crypto', icon: Bitcoin, count: cryptos?.length || 0 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">More Assets</h1>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          <Plus className="h-4 w-4" /> Add {tab === 'insurance' ? 'Policy' : tab === 'esop' ? 'ESOP' : 'Crypto'}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 pb-2">
        {tabs.map(t => (
          <button key={t.key} onClick={() => { setTab(t.key); setShowForm(false); }}
            className={`flex items-center gap-2 rounded-t-lg px-4 py-2 text-sm font-medium transition-colors ${tab === t.key ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}>
            <t.icon className="h-4 w-4" /> {t.label} ({t.count})
          </button>
        ))}
      </div>

      {/* Insurance Tab */}
      {tab === 'insurance' && (
        <div className="space-y-4">
          {showForm && (
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="font-semibold mb-3">Add Insurance Policy</h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <select value={insForm.type} onChange={e => setInsForm({...insForm, type: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm">
                  {['term', 'health', 'ulip', 'endowment', 'motor', 'travel'].map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
                <input value={insForm.provider} onChange={e => setInsForm({...insForm, provider: e.target.value})} placeholder="Provider (LIC, HDFC, etc)" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={insForm.sum_assured} onChange={e => setInsForm({...insForm, sum_assured: e.target.value})} placeholder="Sum Assured" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={insForm.annual_premium} onChange={e => setInsForm({...insForm, annual_premium: e.target.value})} placeholder="Annual Premium" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="date" value={insForm.next_premium_date} onChange={e => setInsForm({...insForm, next_premium_date: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <select value={insForm.tax_section} onChange={e => setInsForm({...insForm, tax_section: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm">
                  <option value="80C">80C</option><option value="80D">80D</option><option value="80CCC">80CCC</option><option value="">None</option>
                </select>
              </div>
              <div className="mt-3 flex gap-2">
                <button onClick={() => addInsurance.mutate()} disabled={!insForm.provider || !insForm.sum_assured} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">Add Policy</button>
                <button onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600">Cancel</button>
              </div>
            </div>
          )}
          {insurance?.map((p: any) => (
            <div key={p.id} className="rounded-xl border border-gray-200 bg-white p-5 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{p.provider}</span>
                  <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700">{p.type}</span>
                  {p.tax_section && <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">{p.tax_section}</span>}
                </div>
                <div className="mt-1 text-sm text-gray-500">
                  Sum: ₹{p.sum_assured.toLocaleString('en-IN')} | Premium: ₹{p.annual_premium.toLocaleString('en-IN')}/{p.premium_frequency}
                  {p.next_premium_date && ` | Next: ${p.next_premium_date}`}
                </div>
              </div>
              <button onClick={() => delInsurance.mutate(p.id)} className="text-gray-300 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
            </div>
          ))}
          {(!insurance || insurance.length === 0) && !showForm && <p className="text-center py-8 text-gray-400">No insurance policies tracked</p>}
        </div>
      )}

      {/* ESOP Tab */}
      {tab === 'esop' && (
        <div className="space-y-4">
          {showForm && (
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="font-semibold mb-3">Add ESOP / RSU</h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <input value={esopForm.company} onChange={e => setEsopForm({...esopForm, company: e.target.value})} placeholder="Company name" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <select value={esopForm.type} onChange={e => setEsopForm({...esopForm, type: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm">
                  <option value="esop">ESOP</option><option value="rsu">RSU</option>
                </select>
                <input type="number" value={esopForm.total_granted} onChange={e => setEsopForm({...esopForm, total_granted: e.target.value})} placeholder="Total granted" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={esopForm.vested} onChange={e => setEsopForm({...esopForm, vested: e.target.value})} placeholder="Vested" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={esopForm.strike_price} onChange={e => setEsopForm({...esopForm, strike_price: e.target.value})} placeholder="Strike price" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={esopForm.current_fmv} onChange={e => setEsopForm({...esopForm, current_fmv: e.target.value})} placeholder="Current FMV" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="date" value={esopForm.next_vesting_date} onChange={e => setEsopForm({...esopForm, next_vesting_date: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input value={esopForm.vesting_schedule} onChange={e => setEsopForm({...esopForm, vesting_schedule: e.target.value})} placeholder="e.g., 25% per year" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
              </div>
              <div className="mt-3 flex gap-2">
                <button onClick={() => addEsop.mutate()} disabled={!esopForm.company || !esopForm.total_granted} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">Add</button>
                <button onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600">Cancel</button>
              </div>
            </div>
          )}
          {esops?.map((e: any) => (
            <div key={e.id} className="rounded-xl border border-gray-200 bg-white p-5 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{e.company}</span>
                  <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-700">{e.type.toUpperCase()}</span>
                </div>
                <div className="mt-1 text-sm text-gray-500">
                  Granted: {e.total_granted} | Vested: {e.vested} | Exercisable: {e.exercisable}
                  {e.strike_price && ` | Strike: ₹${e.strike_price}`}
                  {e.potential_value != null && <span className="text-green-600"> | Value: ₹{e.potential_value.toLocaleString('en-IN')}</span>}
                </div>
                {e.next_vesting_date && <p className="text-xs text-gray-400 mt-1">Next vesting: {e.next_vesting_date}</p>}
              </div>
              <button onClick={() => delEsop.mutate(e.id)} className="text-gray-300 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
            </div>
          ))}
          {(!esops || esops.length === 0) && !showForm && <p className="text-center py-8 text-gray-400">No ESOPs or RSUs tracked</p>}
        </div>
      )}

      {/* Crypto Tab */}
      {tab === 'crypto' && (
        <div className="space-y-4">
          {showForm && (
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="font-semibold mb-3">Add Crypto Holding</h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <input value={cryptoForm.coin} onChange={e => setCryptoForm({...cryptoForm, coin: e.target.value.toUpperCase()})} placeholder="Coin (BTC, ETH, SOL)" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={cryptoForm.quantity} onChange={e => setCryptoForm({...cryptoForm, quantity: e.target.value})} placeholder="Quantity" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input type="number" value={cryptoForm.avg_buy_price_inr} onChange={e => setCryptoForm({...cryptoForm, avg_buy_price_inr: e.target.value})} placeholder="Avg buy price (INR)" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
                <input value={cryptoForm.exchange} onChange={e => setCryptoForm({...cryptoForm, exchange: e.target.value})} placeholder="Exchange (WazirX, CoinSwitch)" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
              </div>
              <div className="mt-3 flex gap-2">
                <button onClick={() => addCrypto.mutate()} disabled={!cryptoForm.coin || !cryptoForm.quantity} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">Add</button>
                <button onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600">Cancel</button>
              </div>
            </div>
          )}
          {cryptos?.map((c: any) => (
            <div key={c.id} className="rounded-xl border border-gray-200 bg-white p-5 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{c.coin}</span>
                  {c.exchange && <span className="text-xs text-gray-400">{c.exchange}</span>}
                </div>
                <div className="mt-1 text-sm text-gray-500">
                  Qty: {c.quantity} | Avg: ₹{c.avg_buy_price_inr.toLocaleString('en-IN')} | Invested: ₹{c.invested.toLocaleString('en-IN')}
                </div>
              </div>
              <button onClick={() => delCrypto.mutate(c.id)} className="text-gray-300 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
            </div>
          ))}
          {(!cryptos || cryptos.length === 0) && !showForm && <p className="text-center py-8 text-gray-400">No crypto holdings tracked</p>}
        </div>
      )}
    </div>
  );
}
