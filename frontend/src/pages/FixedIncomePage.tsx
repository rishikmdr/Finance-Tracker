import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2 } from 'lucide-react';
import api from '../lib/api';
import type { FixedHolding, GoldHolding, PropertyHolding, Liability } from '../types/api';

type Tab = 'fixed' | 'property' | 'gold' | 'liabilities';

const FIXED_TYPES = ['EPF', 'VPF', 'PPF', 'NPS', 'FD', 'SSY', 'bonds'];
const PROPERTY_TYPES = ['residential', 'commercial', 'land'];
const GOLD_TYPES = ['physical', 'digital', 'SGB'];
const LIABILITY_TYPES = ['home_loan', 'car_loan', 'personal_loan', 'education_loan', 'other'];

export function FixedIncomePage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>('fixed');
  const [showForm, setShowForm] = useState(false);

  const { data: fixed = [] } = useQuery<FixedHolding[]>({
    queryKey: ['fixed'], queryFn: () => api.get('/holdings/fixed').then((r) => r.data),
  });
  const { data: properties = [] } = useQuery<PropertyHolding[]>({
    queryKey: ['property'], queryFn: () => api.get('/holdings/property').then((r) => r.data),
  });
  const { data: gold = [] } = useQuery<GoldHolding[]>({
    queryKey: ['gold'], queryFn: () => api.get('/holdings/gold').then((r) => r.data),
  });
  const { data: liabilities = [] } = useQuery<Liability[]>({
    queryKey: ['liabilities'], queryFn: () => api.get('/holdings/liabilities').then((r) => r.data),
  });

  const createFixed = useMutation({
    mutationFn: (data: any) => api.post('/holdings/fixed', data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['fixed'] }); setShowForm(false); },
  });
  const createProperty = useMutation({
    mutationFn: (data: any) => api.post('/holdings/property', data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['property'] }); setShowForm(false); },
  });
  const createGold = useMutation({
    mutationFn: (data: any) => api.post('/holdings/gold', data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['gold'] }); setShowForm(false); },
  });
  const createLiability = useMutation({
    mutationFn: (data: any) => api.post('/holdings/liabilities', data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['liabilities'] }); setShowForm(false); },
  });

  const deleteFixed = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/fixed/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fixed'] }),
  });
  const deleteProperty = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/property/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['property'] }),
  });
  const deleteGold = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/gold/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['gold'] }),
  });
  const deleteLiability = useMutation({
    mutationFn: (id: number) => api.delete(`/holdings/liabilities/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['liabilities'] }),
  });

  const tabs: { key: Tab; label: string; count: number }[] = [
    { key: 'fixed', label: 'Fixed Income', count: fixed.length },
    { key: 'property', label: 'Property', count: properties.length },
    { key: 'gold', label: 'Gold', count: gold.length },
    { key: 'liabilities', label: 'Liabilities', count: liabilities.length },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Fixed Income & Assets</h1>

      <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => { setTab(t.key); setShowForm(false); }}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium ${
              tab === t.key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
            }`}>
            {t.label} ({t.count})
          </button>
        ))}
      </div>

      <button onClick={() => setShowForm(!showForm)}
        className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
        <Plus className="h-4 w-4" /> Add {tabs.find((t) => t.key === tab)?.label}
      </button>

      {/* Fixed Income */}
      {tab === 'fixed' && (
        <>
          {showForm && (
            <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.currentTarget);
              createFixed.mutate({ type: fd.get('type'), name: fd.get('name') || null,
                invested_amount: Number(fd.get('invested_amount')),
                current_value: Number(fd.get('current_value')),
                interest_rate: fd.get('interest_rate') ? Number(fd.get('interest_rate')) : null,
                start_date: fd.get('start_date') || null, maturity_date: fd.get('maturity_date') || null,
              }); }}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <div><label className="block text-sm font-medium text-gray-700">Type</label>
                  <select name="type" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    {FIXED_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select></div>
                <div><label className="block text-sm font-medium text-gray-700">Name</label>
                  <input name="name" placeholder="SBI FD" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Invested</label>
                  <input name="invested_amount" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Current Value</label>
                  <input name="current_value" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Interest %</label>
                  <input name="interest_rate" type="number" step="0.01" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input name="start_date" type="date" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Maturity Date</label>
                  <input name="maturity_date" type="date" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
              </div>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Add</button>
            </form>
          )}
          <div className="space-y-3">
            {fixed.map((f) => (
              <div key={f.id} className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">{f.type}</span>
                    <span className="font-medium text-gray-900">{f.name || f.type}</span>
                  </div>
                  <div className="mt-1 text-sm text-gray-500">
                    Invested: {Number(f.invested_amount).toLocaleString('en-IN')} |
                    Current: {Number(f.current_value).toLocaleString('en-IN')}
                    {f.interest_rate && ` | ${f.interest_rate}%`}
                    {f.maturity_date && ` | Matures: ${f.maturity_date}`}
                  </div>
                </div>
                <button onClick={() => deleteFixed.mutate(f.id)} className="text-gray-400 hover:text-red-500">
                  <Trash2 className="h-4 w-4" /></button>
              </div>
            ))}
            {fixed.length === 0 && <p className="text-center text-gray-400 py-8">No fixed income holdings</p>}
          </div>
        </>
      )}

      {/* Property */}
      {tab === 'property' && (
        <>
          {showForm && (
            <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.currentTarget);
              createProperty.mutate({ name: fd.get('name'), type: fd.get('type'),
                purchase_price: Number(fd.get('purchase_price')),
                estimated_current_value: Number(fd.get('estimated_current_value')),
                purchase_date: fd.get('purchase_date') || null,
                loan_outstanding: fd.get('loan_outstanding') ? Number(fd.get('loan_outstanding')) : null,
                is_shared: fd.get('is_shared') === 'true',
              }); }}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
                <div><label className="block text-sm font-medium text-gray-700">Name</label>
                  <input name="name" required placeholder="2BHK Mumbai" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Type</label>
                  <select name="type" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    {PROPERTY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}</select></div>
                <div><label className="block text-sm font-medium text-gray-700">Purchase Price</label>
                  <input name="purchase_price" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Current Value</label>
                  <input name="estimated_current_value" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Loan Outstanding</label>
                  <input name="loan_outstanding" type="number" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Shared?</label>
                  <select name="is_shared" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    <option value="false">No</option><option value="true">Yes (Family)</option></select></div>
              </div>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Add</button>
            </form>
          )}
          <div className="space-y-3">
            {properties.map((p) => (
              <div key={p.id} className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
                <div>
                  <span className="font-medium text-gray-900">{p.name}</span>
                  <span className="ml-2 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">{p.type}</span>
                  {p.is_shared && <span className="ml-1 rounded-full bg-purple-50 px-2 py-0.5 text-xs font-medium text-purple-700">shared</span>}
                  <div className="mt-1 text-sm text-gray-500">
                    Bought: {Number(p.purchase_price).toLocaleString('en-IN')} |
                    Current: {Number(p.estimated_current_value).toLocaleString('en-IN')}
                    {p.loan_outstanding && ` | Loan: ${Number(p.loan_outstanding).toLocaleString('en-IN')}`}
                  </div>
                </div>
                <button onClick={() => deleteProperty.mutate(p.id)} className="text-gray-400 hover:text-red-500">
                  <Trash2 className="h-4 w-4" /></button>
              </div>
            ))}
            {properties.length === 0 && <p className="text-center text-gray-400 py-8">No properties</p>}
          </div>
        </>
      )}

      {/* Gold */}
      {tab === 'gold' && (
        <>
          {showForm && (
            <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.currentTarget);
              createGold.mutate({ type: fd.get('type'), quantity_grams: Number(fd.get('quantity_grams')),
                purchase_price: Number(fd.get('purchase_price')),
                purchase_date: fd.get('purchase_date') || null,
              }); }}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><label className="block text-sm font-medium text-gray-700">Type</label>
                  <select name="type" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    {GOLD_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}</select></div>
                <div><label className="block text-sm font-medium text-gray-700">Grams</label>
                  <input name="quantity_grams" type="number" step="0.001" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Purchase Price</label>
                  <input name="purchase_price" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Purchase Date</label>
                  <input name="purchase_date" type="date" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
              </div>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Add</button>
            </form>
          )}
          <div className="space-y-3">
            {gold.map((g) => (
              <div key={g.id} className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
                <div>
                  <span className="font-medium text-gray-900">{g.quantity_grams}g {g.type}</span>
                  <div className="mt-1 text-sm text-gray-500">Purchased at {Number(g.purchase_price).toLocaleString('en-IN')}</div>
                </div>
                <button onClick={() => deleteGold.mutate(g.id)} className="text-gray-400 hover:text-red-500">
                  <Trash2 className="h-4 w-4" /></button>
              </div>
            ))}
            {gold.length === 0 && <p className="text-center text-gray-400 py-8">No gold holdings</p>}
          </div>
        </>
      )}

      {/* Liabilities */}
      {tab === 'liabilities' && (
        <>
          {showForm && (
            <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.currentTarget);
              createLiability.mutate({ type: fd.get('type'), name: fd.get('name'),
                principal: Number(fd.get('principal')), outstanding: Number(fd.get('outstanding')),
                interest_rate: Number(fd.get('interest_rate')),
                emi_amount: fd.get('emi_amount') ? Number(fd.get('emi_amount')) : null,
                bank: fd.get('bank') || null,
              }); }}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <div><label className="block text-sm font-medium text-gray-700">Type</label>
                  <select name="type" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    {LIABILITY_TYPES.map((t) => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}</select></div>
                <div><label className="block text-sm font-medium text-gray-700">Name</label>
                  <input name="name" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Principal</label>
                  <input name="principal" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Outstanding</label>
                  <input name="outstanding" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Rate %</label>
                  <input name="interest_rate" type="number" step="0.01" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">EMI</label>
                  <input name="emi_amount" type="number" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Bank</label>
                  <input name="bank" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
              </div>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Add</button>
            </form>
          )}
          <div className="space-y-3">
            {liabilities.map((l) => (
              <div key={l.id} className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
                <div>
                  <span className="font-medium text-gray-900">{l.name}</span>
                  <span className="ml-2 rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">{l.type.replace('_', ' ')}</span>
                  <div className="mt-1 text-sm text-gray-500">
                    Outstanding: {Number(l.outstanding).toLocaleString('en-IN')} |
                    Rate: {l.interest_rate}%
                    {l.emi_amount && ` | EMI: ${Number(l.emi_amount).toLocaleString('en-IN')}`}
                    {l.bank && ` | ${l.bank}`}
                  </div>
                </div>
                <button onClick={() => deleteLiability.mutate(l.id)} className="text-gray-400 hover:text-red-500">
                  <Trash2 className="h-4 w-4" /></button>
              </div>
            ))}
            {liabilities.length === 0 && <p className="text-center text-gray-400 py-8">No liabilities</p>}
          </div>
        </>
      )}
    </div>
  );
}
