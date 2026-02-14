import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './components/layout/AuthProvider';
import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { StocksPage } from './pages/StocksPage';
import { MutualFundsPage } from './pages/MutualFundsPage';
import { FixedIncomePage } from './pages/FixedIncomePage';
import { ExpensesPage } from './pages/ExpensesPage';
import { ChatPage } from './pages/ChatPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={<AppLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/stocks" element={<StocksPage />} />
              <Route path="/mutual-funds" element={<MutualFundsPage />} />
              <Route path="/fixed-income" element={<FixedIncomePage />} />
              <Route path="/expenses" element={<ExpensesPage />} />
              <Route path="/chat" element={<ChatPage />} />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
