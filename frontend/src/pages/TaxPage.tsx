import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Receipt, Plus, Trash2, Scale, Shield, CheckCircle } from 'lucide-react';
import api from '../lib/api';

const SECTIONS = ['80C', '80D_self', '80D_parents', '80CCD_1B', '80G', '80E', '80TTA', '80TTB', 'HRA', '24B'];

function formatINR(v: number) {
  if (v >= 100000) return `${(v / 100000).toFixed(1)}L`;
  if (v >= 1000) return `${(v / 1000).toFixed(0)}K`;
  return v.toFixed(0);
}

export function TaxPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [showCompare, setShowCompare] = useState(false);
  const [income, setIncome] = useState('');
  const [form, setForm] = useState({ section: '80C', description: '', amount: '', financial_year: '', proof_available: false });

  const today = new Date();
  const defaultFY = today.getMonth() < 3
    ? `${today.getFullYear() - 1}-${String(today.getFullYear()).slice(2)}`
    : `${today.getFullYear()}-${String(today.getFullYear() + 1).slice(2)}`;

  const { data: deductions, isLoading } = useQuery({
    queryKey: ['tax-deductions', defaultFY],
    queryFn: () => api.get(`/tax/deductions?fy=${defaultFY}`).then(r => r.data),
  });

  const { data: comparison } = useQuery({
    queryKey: ['tax-comparison', income, deductions?.total_deductions],
    queryFn: () => api.get(`/tax/regime-comparison?annual_income=${income}&total_deductions=${deductions?.total_deductions || 0}`).then(r => r.data),
    enabled: !!income && showCompare,
  });

  const addDeduction = useMutation({
    mutationFn: () => api.post('/tax/deductions', { ...form, amount: parseFloat(form.amount), financial_year: form.financial_year || defaultFY }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tax-deductions'] });
      setShowForm(false);
      setForm({ section: '80C', description: '', amount: '', financial_year: '', proof_available: false });
    },
  });

  const deleteDeduction = useMutation({
    mutationFn: (id: number) => api.delete(`/tax/deductions/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tax-deductions'] }),
  });

  if (isLoading) {
    return <div className="flex items-center justify-center py-20"><div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tax Planning</h1>
          <p className="text-sm text-gray-500">FY {defaultFY} — Track deductions and compare regimes</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowCompare(!showCompare)} className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">
            <Scale className="h-4 w-4" /> Compare Regimes
          </button>
          <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add Deduction
          </button>
        </div>
      </div>

      {/* Total Summary */}
      <div className="rounded-xl border border-gray-200 bg-gradient-to-r from-green-50 to-blue-50 p-6">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="h-6 w-6 text-green-600" />
          <span className="text-lg font-semibold text-gray-900">Total Deductions: ₹{(deductions?.total_deductions || 0).toLocaleString('en-IN')}</span>
        </div>
        <p className="text-sm text-gray-500">Across {deductions?.sections?.length || 0} sections</p>
      </div>

      {/* Regime Comparison */}
      {showCompare && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="text-lg font-semibold mb-4">Old vs New Tax Regime</h3>
          <div className="mb-4">
            <label className="text-sm text-gray-600">Annual Gross Income</label>
            <input type="number" value={income} onChange={e => setIncome(e.target.value)} placeholder="e.g. 1500000" className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
          </div>
          {comparison && (
            <div className="grid grid-cols-2 gap-4">
              <div className={`rounded-xl border-2 p-4 ${comparison.recommended === 'old' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}>
                <h4 className="font-semibold text-gray-900">Old Regime</h4>
                <p className="text-sm text-gray-500">Taxable: ₹{comparison.old_regime.taxable_income.toLocaleString('en-IN')}</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">₹{comparison.old_regime.total.toLocaleString('en-IN')}</p>
                <p className="text-xs text-gray-400">Tax + 4% cess</p>
                {comparison.recommended === 'old' && <p className="mt-2 text-sm font-medium text-green-600 flex items-center gap-1"><CheckCircle className="h-4 w-4" /> Recommended — saves ₹{comparison.savings_with_old.toLocaleString('en-IN')}</p>}
              </div>
              <div className={`rounded-xl border-2 p-4 ${comparison.recommended === 'new' ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}>
                <h4 className="font-semibold text-gray-900">New Regime</h4>
                <p className="text-sm text-gray-500">Taxable: ₹{comparison.new_regime.taxable_income.toLocaleString('en-IN')}</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">₹{comparison.new_regime.total.toLocaleString('en-IN')}</p>
                <p className="text-xs text-gray-400">Tax + 4% cess</p>
                {comparison.recommended === 'new' && <p className="mt-2 text-sm font-medium text-green-600 flex items-center gap-1"><CheckCircle className="h-4 w-4" /> Recommended — saves ₹{comparison.savings_with_new.toLocaleString('en-IN')}</p>}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add Form */}
      {showForm && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="text-lg font-semibold mb-4">Add Tax Deduction</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <select value={form.section} onChange={e => setForm({...form, section: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm">
              {SECTIONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="e.g., ELSS fund, PPF" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <input type="number" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="Amount" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input type="checkbox" checked={form.proof_available} onChange={e => setForm({...form, proof_available: e.target.checked})} className="rounded" />
              Proof available
            </label>
          </div>
          <div className="mt-4 flex gap-3">
            <button onClick={() => addDeduction.mutate()} disabled={!form.description || !form.amount} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">Add</button>
            <button onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600">Cancel</button>
          </div>
        </div>
      )}

      {/* Sections breakdown */}
      <div className="space-y-4">
        {deductions?.sections?.map((section: any) => (
          <div key={section.section} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-gray-900">Section {section.section}</h3>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>Total: ₹{section.total.toLocaleString('en-IN')}</span>
                  {section.limit && <span>Limit: ₹{section.limit.toLocaleString('en-IN')}</span>}
                  {section.remaining != null && <span className={section.remaining > 0 ? 'text-green-600' : 'text-gray-400'}>Remaining: ₹{section.remaining.toLocaleString('en-IN')}</span>}
                </div>
              </div>
              {section.utilized_pct != null && (
                <span className={`text-sm font-medium ${section.utilized_pct >= 100 ? 'text-green-600' : 'text-amber-600'}`}>{section.utilized_pct}%</span>
              )}
            </div>
            {section.limit && (
              <div className="h-2 rounded-full bg-gray-100 mb-3">
                <div className={`h-2 rounded-full ${section.utilized_pct >= 100 ? 'bg-green-500' : 'bg-blue-500'}`} style={{ width: `${Math.min(100, section.utilized_pct || 0)}%` }} />
              </div>
            )}
            <div className="space-y-2">
              {section.items.map((item: any) => (
                <div key={item.id} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-700">{item.description}</span>
                    {item.proof_available && <CheckCircle className="h-3.5 w-3.5 text-green-500" />}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-medium">₹{item.amount.toLocaleString('en-IN')}</span>
                    <button onClick={() => deleteDeduction.mutate(item.id)} className="text-gray-300 hover:text-red-500"><Trash2 className="h-3.5 w-3.5" /></button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
        {(!deductions?.sections || deductions.sections.length === 0) && !showForm && (
          <div className="text-center py-12 text-gray-400">
            <Receipt className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No deductions tracked yet. Add your 80C, 80D investments!</p>
          </div>
        )}
      </div>
    </div>
  );
}
