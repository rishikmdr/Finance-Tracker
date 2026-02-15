import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Settings,
  Key,
  Eye,
  EyeOff,
  Save,
  Trash2,
  Shield,
  Target,
  DollarSign,
  Bell,
  Palette,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import api from '../lib/api';

interface UserSettings {
  has_api_key: boolean;
  api_key_preview: string | null;
  currency: string;
  theme: string;
  notifications_enabled: boolean;
  monthly_budget: number | null;
  emergency_fund_target: number | null;
  retirement_age: number | null;
  risk_profile: string | null;
  notes: string | null;
}

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    monthly_budget: '',
    emergency_fund_target: '',
    retirement_age: '',
    risk_profile: '',
    notifications_enabled: true,
    theme: 'light',
  });

  const { data: settings, isLoading } = useQuery<UserSettings>({
    queryKey: ['settings'],
    queryFn: () => api.get('/settings').then((r) => r.data),
  });

  useEffect(() => {
    if (settings) {
      setForm({
        monthly_budget: settings.monthly_budget?.toString() || '',
        emergency_fund_target: settings.emergency_fund_target?.toString() || '',
        retirement_age: settings.retirement_age?.toString() || '',
        risk_profile: settings.risk_profile || '',
        notifications_enabled: settings.notifications_enabled,
        theme: settings.theme,
      });
    }
  }, [settings]);

  const saveKey = useMutation({
    mutationFn: () => api.put('/settings', { anthropic_api_key: apiKey }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      setApiKey('');
      setSaved(true);
      setError('');
      setTimeout(() => setSaved(false), 3000);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to save API key');
    },
  });

  const deleteKey = useMutation({
    mutationFn: () => api.delete('/settings/api-key'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  const saveSettings = useMutation({
    mutationFn: () =>
      api.put('/settings', {
        monthly_budget: form.monthly_budget ? parseFloat(form.monthly_budget) : null,
        emergency_fund_target: form.emergency_fund_target ? parseFloat(form.emergency_fund_target) : null,
        retirement_age: form.retirement_age ? parseInt(form.retirement_age) : null,
        risk_profile: form.risk_profile || null,
        notifications_enabled: form.notifications_enabled,
        theme: form.theme,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <Settings className="h-7 w-7 text-gray-700" />
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      </div>

      {saved && (
        <div className="flex items-center gap-2 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
          <CheckCircle className="h-4 w-4" />
          Settings saved successfully!
        </div>
      )}

      {/* API Key Section */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="rounded-lg bg-purple-50 p-2">
            <Key className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">AI API Key</h2>
            <p className="text-sm text-gray-500">
              Add your Anthropic API key to enable AI portfolio analysis and chatbot
            </p>
          </div>
        </div>

        {settings?.has_api_key ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg bg-green-50 border border-green-200 px-4 py-3">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">API key configured</span>
                <span className="text-sm text-green-600">{settings.api_key_preview}</span>
              </div>
              <button
                onClick={() => deleteKey.mutate()}
                className="flex items-center gap-1 text-sm text-red-600 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
                Remove
              </button>
            </div>
            <p className="text-xs text-gray-400">
              Your key is stored securely. AI features are now enabled.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
              <AlertCircle className="h-4 w-4" />
              No API key configured. AI features are disabled.
            </div>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setError('');
                }}
                placeholder="sk-ant-api03-..."
                className="w-full rounded-lg border border-gray-300 px-4 py-3 pr-20 text-sm font-mono focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex items-center justify-between">
              <p className="text-xs text-gray-400">
                Get your key from{' '}
                <a
                  href="https://console.anthropic.com/settings/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  console.anthropic.com
                </a>
              </p>
              <button
                onClick={() => saveKey.mutate()}
                disabled={!apiKey.trim() || saveKey.isPending}
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                <Save className="h-4 w-4" />
                {saveKey.isPending ? 'Saving...' : 'Save Key'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Financial Profile */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-lg bg-blue-50 p-2">
            <Target className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Financial Profile</h2>
            <p className="text-sm text-gray-500">
              Help the AI advisor understand your goals and risk appetite
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <DollarSign className="inline h-4 w-4 mr-1" />
              Monthly Budget
            </label>
            <input
              type="number"
              value={form.monthly_budget}
              onChange={(e) => setForm({ ...form, monthly_budget: e.target.value })}
              placeholder="e.g. 50000"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Shield className="inline h-4 w-4 mr-1" />
              Emergency Fund Target
            </label>
            <input
              type="number"
              value={form.emergency_fund_target}
              onChange={(e) => setForm({ ...form, emergency_fund_target: e.target.value })}
              placeholder="e.g. 500000"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Retirement Age</label>
            <input
              type="number"
              value={form.retirement_age}
              onChange={(e) => setForm({ ...form, retirement_age: e.target.value })}
              placeholder="e.g. 55"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Risk Profile</label>
            <select
              value={form.risk_profile}
              onChange={(e) => setForm({ ...form, risk_profile: e.target.value })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Select...</option>
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <Bell className="h-4 w-4" />
              <input
                type="checkbox"
                checked={form.notifications_enabled}
                onChange={(e) => setForm({ ...form, notifications_enabled: e.target.checked })}
                className="rounded border-gray-300"
              />
              Notifications
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <Palette className="h-4 w-4" />
              <select
                value={form.theme}
                onChange={(e) => setForm({ ...form, theme: e.target.value })}
                className="rounded border-gray-300 text-sm"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>
          </div>
          <button
            onClick={() => saveSettings.mutate()}
            disabled={saveSettings.isPending}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {saveSettings.isPending ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {/* Data Management */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Data & Export</h2>
        <div className="flex gap-3">
          <button
            onClick={async () => {
              const { data } = await api.get('/portfolio/export');
              const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `finance-tracker-export-${new Date().toISOString().split('T')[0]}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Export Portfolio JSON
          </button>
        </div>
      </div>
    </div>
  );
}
