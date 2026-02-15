import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Target, Plus, Trash2, TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import api from '../lib/api';

const CATEGORIES = ['retirement', 'education', 'house', 'marriage', 'emergency', 'travel', 'car', 'wealth', 'other'];

function formatINR(value: number): string {
  if (value >= 10000000) return `${(value / 10000000).toFixed(2)} Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(1)} L`;
  if (value >= 1000) return `${(value / 1000).toFixed(0)} K`;
  return `${value.toFixed(0)}`;
}

interface Goal {
  id: number; name: string; description: string | null;
  target_amount: number; current_amount: number; target_date: string;
  priority: string; status: string; category: string | null;
  progress_pct: number; months_left: number; monthly_sip_needed: number;
  inflation_adjusted_target: number; on_track: boolean;
}

export function GoalsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: '', target_amount: '', current_amount: '0', target_date: '',
    priority: 'medium', category: '', expected_return_pct: '12', inflation_pct: '6', description: '',
  });

  const { data: goals, isLoading } = useQuery<Goal[]>({
    queryKey: ['goals'],
    queryFn: () => api.get('/goals').then(r => r.data),
  });

  const createGoal = useMutation({
    mutationFn: () => api.post('/goals', {
      ...form,
      target_amount: parseFloat(form.target_amount),
      current_amount: parseFloat(form.current_amount || '0'),
      expected_return_pct: parseFloat(form.expected_return_pct),
      inflation_pct: parseFloat(form.inflation_pct),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      setShowForm(false);
      setForm({ name: '', target_amount: '', current_amount: '0', target_date: '', priority: 'medium', category: '', expected_return_pct: '12', inflation_pct: '6', description: '' });
    },
  });

  const deleteGoal = useMutation({
    mutationFn: (id: number) => api.delete(`/goals/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['goals'] }),
  });

  const updateGoal = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.put(`/goals/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['goals'] }),
  });

  if (isLoading) {
    return <div className="flex items-center justify-center py-20"><div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>;
  }

  const activeGoals = goals?.filter(g => g.status === 'active') || [];
  const totalTarget = activeGoals.reduce((s, g) => s + g.target_amount, 0);
  const totalCurrent = activeGoals.reduce((s, g) => s + g.current_amount, 0);
  const totalSIPNeeded = activeGoals.reduce((s, g) => s + g.monthly_sip_needed, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Goals</h1>
          <p className="text-sm text-gray-500">Track progress towards your life goals</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          <Plus className="h-4 w-4" /> Add Goal
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <span className="text-sm text-gray-500">Total Target</span>
          <p className="text-2xl font-bold text-gray-900">{formatINR(totalTarget)}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <span className="text-sm text-gray-500">Currently Saved</span>
          <p className="text-2xl font-bold text-green-600">{formatINR(totalCurrent)}</p>
          <p className="text-xs text-gray-400">{totalTarget > 0 ? `${(totalCurrent / totalTarget * 100).toFixed(1)}% of target` : ''}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <span className="text-sm text-gray-500">Monthly SIP Needed</span>
          <p className="text-2xl font-bold text-blue-600">{formatINR(totalSIPNeeded)}</p>
          <p className="text-xs text-gray-400">across all active goals</p>
        </div>
      </div>

      {/* Add Goal Form */}
      {showForm && (
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <h3 className="text-lg font-semibold mb-4">New Goal</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Goal name (e.g., Retire at 50)" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <select value={form.category} onChange={e => setForm({...form, category: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="">Category</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select>
            <input type="number" value={form.target_amount} onChange={e => setForm({...form, target_amount: e.target.value})} placeholder="Target amount" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <input type="number" value={form.current_amount} onChange={e => setForm({...form, current_amount: e.target.value})} placeholder="Already saved" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <input type="date" value={form.target_date} onChange={e => setForm({...form, target_date: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} className="rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
              <option value="critical">Critical</option>
            </select>
            <input type="number" value={form.expected_return_pct} onChange={e => setForm({...form, expected_return_pct: e.target.value})} placeholder="Expected return %" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            <input type="number" value={form.inflation_pct} onChange={e => setForm({...form, inflation_pct: e.target.value})} placeholder="Inflation %" className="rounded-lg border border-gray-300 px-3 py-2 text-sm" />
          </div>
          <div className="mt-4 flex gap-3">
            <button onClick={() => createGoal.mutate()} disabled={!form.name || !form.target_amount || !form.target_date} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
              Create Goal
            </button>
            <button onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">Cancel</button>
          </div>
        </div>
      )}

      {/* Goals List */}
      <div className="space-y-4">
        {activeGoals.length === 0 && !showForm && (
          <div className="text-center py-12 text-gray-400">
            <Target className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No goals yet. Add your first financial goal!</p>
          </div>
        )}
        {activeGoals.map(goal => (
          <div key={goal.id} className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold text-gray-900">{goal.name}</h3>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    goal.priority === 'critical' ? 'bg-red-100 text-red-700' :
                    goal.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                    goal.priority === 'medium' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}>{goal.priority}</span>
                  {goal.category && <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{goal.category}</span>}
                  {goal.on_track ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-amber-500" />
                  )}
                </div>
                <div className="mt-3 flex items-center gap-6 text-sm text-gray-500">
                  <span><Target className="inline h-4 w-4 mr-1" />Target: {formatINR(goal.target_amount)}</span>
                  <span><TrendingUp className="inline h-4 w-4 mr-1" />Saved: {formatINR(goal.current_amount)}</span>
                  <span><Clock className="inline h-4 w-4 mr-1" />{goal.months_left} months left</span>
                  <span>SIP needed: {formatINR(goal.monthly_sip_needed)}/mo</span>
                </div>
                {/* Progress bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{goal.progress_pct.toFixed(1)}% complete</span>
                    <span>Gap: {formatINR(goal.target_amount - goal.current_amount)}</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-gray-100">
                    <div className={`h-2.5 rounded-full transition-all ${goal.on_track ? 'bg-green-500' : 'bg-amber-500'}`} style={{ width: `${Math.min(100, goal.progress_pct)}%` }} />
                  </div>
                </div>
              </div>
              <div className="flex gap-2 ml-4">
                <button onClick={() => {
                  const amt = prompt('Update saved amount:', goal.current_amount.toString());
                  if (amt) updateGoal.mutate({ id: goal.id, data: { current_amount: parseFloat(amt) } });
                }} className="rounded-lg border border-gray-200 p-2 text-gray-400 hover:text-blue-600 hover:border-blue-200">
                  <TrendingUp className="h-4 w-4" />
                </button>
                <button onClick={() => deleteGoal.mutate(goal.id)} className="rounded-lg border border-gray-200 p-2 text-gray-400 hover:text-red-600 hover:border-red-200">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
