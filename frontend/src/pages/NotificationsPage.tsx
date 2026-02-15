import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Check, CheckCheck, RefreshCw, AlertTriangle, Info, Clock, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../lib/api';

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  action_url: string | null;
  created_at: string;
}

const typeIcon = (type: string) => {
  switch (type) {
    case 'alert': return <AlertTriangle className="h-5 w-5 text-red-500" />;
    case 'warning': return <Shield className="h-5 w-5 text-amber-500" />;
    case 'reminder': return <Clock className="h-5 w-5 text-blue-500" />;
    default: return <Info className="h-5 w-5 text-gray-500" />;
  }
};

const typeBg = (type: string, isRead: boolean) => {
  if (isRead) return 'bg-white';
  switch (type) {
    case 'alert': return 'bg-red-50 border-red-200';
    case 'warning': return 'bg-amber-50 border-amber-200';
    case 'reminder': return 'bg-blue-50 border-blue-200';
    default: return 'bg-gray-50 border-gray-200';
  }
};

export function NotificationsPage() {
  const queryClient = useQueryClient();

  const { data: notifications, isLoading } = useQuery<Notification[]>({
    queryKey: ['notifications'],
    queryFn: () => api.get('/notifications').then((r) => r.data),
  });

  const markRead = useMutation({
    mutationFn: (id: number) => api.put(`/notifications/${id}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notifications-count'] });
    },
  });

  const markAllRead = useMutation({
    mutationFn: () => api.put('/notifications/read-all'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notifications-count'] });
    },
  });

  const generateAlerts = useMutation({
    mutationFn: () => api.post('/notifications/generate'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notifications-count'] });
    },
  });

  const unreadCount = notifications?.filter((n) => !n.is_read).length || 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="h-7 w-7 text-gray-700" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
            <p className="text-sm text-gray-500">
              {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => generateAlerts.mutate()}
            disabled={generateAlerts.isPending}
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
          >
            <RefreshCw className={`h-4 w-4 ${generateAlerts.isPending ? 'animate-spin' : ''}`} />
            Scan for Alerts
          </button>
          {unreadCount > 0 && (
            <button
              onClick={() => markAllRead.mutate()}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
            >
              <CheckCheck className="h-4 w-4" />
              Mark All Read
            </button>
          )}
        </div>
      </div>

      {!notifications || notifications.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
          <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700">No notifications</h2>
          <p className="mt-2 text-sm text-gray-500">
            Click "Scan for Alerts" to check for SIP reminders, FD maturity, insurance premiums, and more.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`rounded-xl border p-4 transition-colors ${typeBg(n.type, n.is_read)} ${
                n.is_read ? 'border-gray-200' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{typeIcon(n.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className={`text-sm font-semibold ${n.is_read ? 'text-gray-600' : 'text-gray-900'}`}>
                      {n.title}
                    </h3>
                    <span className="text-xs text-gray-400 whitespace-nowrap">
                      {new Date(n.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                      })}
                    </span>
                  </div>
                  <p className={`mt-1 text-sm ${n.is_read ? 'text-gray-400' : 'text-gray-600'}`}>
                    {n.message}
                  </p>
                  <div className="mt-2 flex items-center gap-3">
                    {n.action_url && (
                      <Link
                        to={n.action_url}
                        className="text-xs font-medium text-blue-600 hover:text-blue-700"
                      >
                        View details
                      </Link>
                    )}
                    {!n.is_read && (
                      <button
                        onClick={() => markRead.mutate(n.id)}
                        className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600"
                      >
                        <Check className="h-3 w-3" />
                        Mark read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
