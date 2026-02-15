import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  Wallet,
  ArrowDownUp,
  MessageCircle,
  LogOut,
  Users,
  LineChart,
  Settings,
  Target,
  Receipt,
  Layers,
  Bell,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import api from '../../lib/api';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/stocks', icon: TrendingUp, label: 'Stocks' },
  { to: '/mutual-funds', icon: BarChart3, label: 'Mutual Funds' },
  { to: '/fixed-income', icon: Wallet, label: 'Fixed Income' },
  { to: '/more-assets', icon: Layers, label: 'More Assets' },
  { to: '/expenses', icon: ArrowDownUp, label: 'Expenses' },
  { to: '/goals', icon: Target, label: 'Goals' },
  { to: '/tax', icon: Receipt, label: 'Tax Planning' },
  { to: '/analytics', icon: LineChart, label: 'Analytics' },
  { to: '/chat', icon: MessageCircle, label: 'AI Advisor' },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  const { data: notifications } = useQuery({
    queryKey: ['notifications-count'],
    queryFn: () => api.get('/notifications?unread_only=true').then(r => r.data),
    refetchInterval: 60000,
  });

  const unreadCount = notifications?.length || 0;

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-gray-200 bg-white">
      <div className="border-b border-gray-200 p-6">
        <h1 className="text-xl font-bold text-gray-900">Finance Tracker</h1>
        <p className="mt-1 text-sm text-gray-500">{user?.name}</p>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}

        {user?.family_id && (
          <NavLink
            to="/family"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Users className="h-5 w-5" />
            Family View
          </NavLink>
        )}
      </nav>

      <div className="border-t border-gray-200 p-4 space-y-1">
        {unreadCount > 0 && (
          <div className="flex items-center gap-2 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">
            <Bell className="h-4 w-4" />
            {unreadCount} new alert{unreadCount > 1 ? 's' : ''}
          </div>
        )}
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`
          }
        >
          <Settings className="h-5 w-5" />
          Settings
        </NavLink>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50 hover:text-gray-900"
        >
          <LogOut className="h-5 w-5" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
