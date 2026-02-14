import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Upload } from 'lucide-react';
import api from '../lib/api';
import type { Expense, Income } from '../types/api';

export function ExpensesPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<'expenses' | 'income'>('expenses');
  const [showForm, setShowForm] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  const { data: expenses = [] } = useQuery<Expense[]>({
    queryKey: ['expenses', month, year],
    queryFn: () => api.get('/expenses', { params: { month, year } }).then((r) => r.data),
  });

  const { data: incomes = [] } = useQuery<Income[]>({
    queryKey: ['income', month, year],
    queryFn: () => api.get('/income', { params: { month, year } }).then((r) => r.data),
  });

  const createExpense = useMutation({
    mutationFn: (data: any) => api.post('/expenses', data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['expenses'] }); setShowForm(false); },
  });

  const createIncome = useMutation({
    mutationFn: (data: any) => api.post('/income', data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['income'] }); setShowForm(false); },
  });

  const deleteExpense = useMutation({
    mutationFn: (id: number) => api.delete(`/expenses/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['expenses'] }),
  });

  const deleteIncome = useMutation({
    mutationFn: (id: number) => api.delete(`/income/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['income'] }),
  });

  const handleCSVUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const { data } = await api.post('/expenses/import/axio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImportResult(data);
      queryClient.invalidateQueries({ queryKey: ['expenses'] });
    } catch (err: any) {
      setImportResult({ error: err.response?.data?.detail || 'Import failed' });
    }
  };

  const totalExpenses = expenses.reduce((s, e) => s + e.amount, 0);
  const totalIncome = incomes.reduce((s, i) => s + i.amount, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Expenses & Income</h1>
        <div className="flex items-center gap-2">
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm">
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {new Date(2000, i).toLocaleString('en', { month: 'long' })}
              </option>
            ))}
          </select>
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm">
            {[2024, 2025, 2026].map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Income</p>
          <p className="text-xl font-bold text-green-600">{totalIncome.toLocaleString('en-IN')}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Expenses</p>
          <p className="text-xl font-bold text-red-600">{totalExpenses.toLocaleString('en-IN')}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Savings</p>
          <p className={`text-xl font-bold ${totalIncome - totalExpenses >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {(totalIncome - totalExpenses).toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
        <button onClick={() => { setTab('expenses'); setShowForm(false); }}
          className={`flex-1 rounded-md px-4 py-2 text-sm font-medium ${tab === 'expenses' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'}`}>
          Expenses ({expenses.length})
        </button>
        <button onClick={() => { setTab('income'); setShowForm(false); }}
          className={`flex-1 rounded-md px-4 py-2 text-sm font-medium ${tab === 'income' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'}`}>
          Income ({incomes.length})
        </button>
      </div>

      {tab === 'expenses' && (
        <>
          <div className="flex gap-2">
            <button onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
              <Plus className="h-4 w-4" /> Add Expense
            </button>
            <label className="flex cursor-pointer items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">
              <Upload className="h-4 w-4" /> Import Axio CSV
              <input ref={fileRef} type="file" accept=".csv" onChange={handleCSVUpload} className="hidden" />
            </label>
          </div>

          {importResult && (
            <div className={`rounded-lg p-4 text-sm ${importResult.error ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
              {importResult.error || `Imported ${importResult.new_rows} new transactions (${importResult.duplicate_rows} duplicates skipped)`}
              <button onClick={() => setImportResult(null)} className="ml-2 underline">dismiss</button>
            </div>
          )}

          {showForm && (
            <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.currentTarget);
              createExpense.mutate({ date: fd.get('date'), amount: Number(fd.get('amount')),
                description: fd.get('description') || null }); }}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div><label className="block text-sm font-medium text-gray-700">Date</label>
                  <input name="date" type="date" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Amount</label>
                  <input name="amount" type="number" step="0.01" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Description</label>
                  <input name="description" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
              </div>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Add</button>
            </form>
          )}

          <div className="space-y-2">
            {expenses.map((e) => (
              <div key={e.id} className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3">
                <div>
                  <span className="text-sm font-medium text-gray-900">{e.description || 'Expense'}</span>
                  <span className="ml-2 text-xs text-gray-400">{e.date}</span>
                  {e.import_source !== 'manual' && (
                    <span className="ml-2 rounded-full bg-purple-50 px-2 py-0.5 text-xs text-purple-600">{e.import_source}</span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-medium text-red-600">{Number(e.amount).toLocaleString('en-IN')}</span>
                  <button onClick={() => deleteExpense.mutate(e.id)} className="text-gray-400 hover:text-red-500">
                    <Trash2 className="h-4 w-4" /></button>
                </div>
              </div>
            ))}
            {expenses.length === 0 && <p className="text-center text-gray-400 py-8">No expenses this month</p>}
          </div>
        </>
      )}

      {tab === 'income' && (
        <>
          <button onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add Income
          </button>

          {showForm && (
            <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.currentTarget);
              createIncome.mutate({ date: fd.get('date'), amount: Number(fd.get('amount')),
                source: fd.get('source'), earner: fd.get('earner'), notes: fd.get('notes') || null }); }}
              className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
                <div><label className="block text-sm font-medium text-gray-700">Date</label>
                  <input name="date" type="date" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Amount</label>
                  <input name="amount" type="number" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-sm font-medium text-gray-700">Source</label>
                  <select name="source" required className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    <option value="salary">Salary</option><option value="rental">Rental</option>
                    <option value="dividend">Dividend</option><option value="interest">Interest</option>
                    <option value="freelance">Freelance</option><option value="other">Other</option>
                  </select></div>
                <div><label className="block text-sm font-medium text-gray-700">Earner</label>
                  <select name="earner" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                    <option value="self">Self</option><option value="spouse">Spouse</option>
                  </select></div>
                <div><label className="block text-sm font-medium text-gray-700">Notes</label>
                  <input name="notes" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" /></div>
              </div>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Add</button>
            </form>
          )}

          <div className="space-y-2">
            {incomes.map((i) => (
              <div key={i.id} className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3">
                <div>
                  <span className="text-sm font-medium text-gray-900 capitalize">{i.source}</span>
                  <span className="ml-2 rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-600">{i.earner}</span>
                  <span className="ml-2 text-xs text-gray-400">{i.date}</span>
                  {i.notes && <span className="ml-2 text-xs text-gray-400">— {i.notes}</span>}
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-medium text-green-600">{Number(i.amount).toLocaleString('en-IN')}</span>
                  <button onClick={() => deleteIncome.mutate(i.id)} className="text-gray-400 hover:text-red-500">
                    <Trash2 className="h-4 w-4" /></button>
                </div>
              </div>
            ))}
            {incomes.length === 0 && <p className="text-center text-gray-400 py-8">No income this month</p>}
          </div>
        </>
      )}
    </div>
  );
}
