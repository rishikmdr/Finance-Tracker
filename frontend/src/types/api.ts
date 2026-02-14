// User & Auth
export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  family_id: number | null;
  family_role: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Family {
  id: number;
  name: string;
  members: User[];
  created_at: string;
}

// Holdings
export interface StockHolding {
  id: number;
  symbol: string;
  exchange: 'NSE' | 'BSE';
  investment_type: 'long_term' | 'swing' | 'positional' | 'intraday' | 'ipo';
  quantity: number;
  avg_buy_price: number;
  buy_date: string;
  broker: string | null;
  notes: string | null;
  created_at: string;
  current_price?: number;
  day_change_pct?: number;
  current_value?: number;
  pnl?: number;
  pnl_pct?: number;
}

export interface MFHolding {
  id: number;
  scheme_code: string;
  scheme_name: string;
  category: string | null;
  units: number;
  avg_nav: number;
  investment_mode: 'sip' | 'lumpsum';
  buy_date: string;
  folio_number: string | null;
  platform: string | null;
  created_at: string;
  current_nav?: number;
  current_value?: number;
  pnl?: number;
  pnl_pct?: number;
}

export interface SIP {
  id: number;
  scheme_code: string;
  scheme_name: string;
  amount: number;
  day_of_month: number;
  frequency: 'monthly' | 'quarterly';
  start_date: string;
  end_date: string | null;
  step_up_percent: number | null;
  is_active: boolean;
  created_at: string;
}

export interface FixedHolding {
  id: number;
  type: string;
  name: string | null;
  invested_amount: number;
  current_value: number;
  interest_rate: number | null;
  start_date: string | null;
  maturity_date: string | null;
  notes: string | null;
}

export interface PropertyHolding {
  id: number;
  name: string;
  type: string;
  purchase_price: number;
  purchase_date: string | null;
  estimated_current_value: number;
  loan_outstanding: number | null;
  is_shared: boolean;
  notes: string | null;
}

export interface GoldHolding {
  id: number;
  type: 'physical' | 'digital' | 'SGB';
  quantity_grams: number;
  purchase_price: number;
  purchase_date: string | null;
  current_price_per_gram?: number;
  current_value?: number;
  pnl?: number;
}

export interface Liability {
  id: number;
  type: string;
  name: string;
  principal: number;
  outstanding: number;
  interest_rate: number;
  emi_amount: number | null;
  start_date: string | null;
  end_date: string | null;
  bank: string | null;
}

// Expenses & Income
export interface Expense {
  id: number;
  date: string;
  amount: number;
  category_id: number | null;
  category_name: string | null;
  description: string | null;
  import_source: string;
  created_at: string;
}

export interface Income {
  id: number;
  date: string;
  amount: number;
  source: string;
  earner: string;
  notes: string | null;
  created_at: string;
}

export interface ExpenseCategory {
  id: number;
  name: string;
  parent_id: number | null;
  icon: string | null;
}

// Dashboard
export interface DashboardSummary {
  net_worth: number;
  total_assets: number;
  total_liabilities: number;
  asset_breakdown: {
    stocks: number;
    mutual_funds: number;
    fixed_income: number;
    property: number;
    gold: number;
  };
  asset_allocation_pct: {
    equity: number;
    fixed_income: number;
    real_estate: number;
    gold: number;
  };
  month_summary: {
    income: number;
    expenses: number;
    savings: number;
  };
  counts: Record<string, number>;
}
