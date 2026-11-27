import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  Bell,
  Menu,
  Plus,
  Calendar,
  ShoppingCart,
  AlertTriangle,
  CheckCircle2,
  Info,
  X,
} from 'lucide-react';
import { useAuth } from './AuthContext';

export const TopHeader = ({
  onOpenMobileMenu,
  searchQuery = '',
  onSearchChange,
  onSearchSubmit,
  dateRange = 'weekly',
  onDateRangeChange,
  onOpenLogModal,
  onNavigate,
  onOpenAuth,
  notifications = [],
  cartCount = 0,
  pageTitle = 'Food Analytics & Nutrition Overview',
}) => {
  const { displayName, isAuthenticated } = useAuth();
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);

  useEffect(() => {
    const handleOutside = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  const todayStr = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const warningCount = notifications.filter((n) => n.severity === 'warning').length;

  return (
    <header className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border-b border-[#D8C5FF] px-4 sm:px-6 lg:px-8 py-3">
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-3">
        {/* Left: Hamburger + Welcome + Date */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={onOpenMobileMenu}
              className="lg:hidden p-2 rounded-xl border border-[#D8C5FF] text-[#351078] hover:bg-[#F2ECFF]"
              aria-label="Open navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="font-display font-bold text-base sm:text-lg text-[#230852] truncate">
                  Welcome back, {displayName}
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#EEF8FC] text-[#230852] text-[11px] font-semibold border border-[#ADD8E6]">
                  <Calendar className="w-3 h-3 text-[#351078]" />
                  <span>{todayStr}</span>
                </span>
              </div>
              <p className="text-xs text-[#5B4B7A] truncate">{pageTitle}</p>
            </div>
          </div>

          <button
            type="button"
            onClick={onOpenLogModal}
            className="sm:hidden px-3 py-2 rounded-xl bg-[#351078] text-white text-xs font-bold flex items-center gap-1 shadow-xs"
          >
            <Plus className="w-4 h-4 text-[#C6FF00]" />
            <span>Log</span>
          </button>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-2.5 flex-wrap justify-between xl:justify-end">
          {/* Search Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (onSearchSubmit) onSearchSubmit(searchQuery);
            }}
            className="relative flex-1 sm:flex-initial sm:w-56 lg:w-60"
          >
            <Search className="w-4 h-4 text-[#5B4B7A] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
              placeholder="Search foods, nutrients..."
              className="w-full pl-9 pr-7 py-2 rounded-xl bg-[#F2ECFF]/70 border border-[#D8C5FF] text-xs sm:text-sm text-[#230852] placeholder:text-[#5B4B7A] focus:outline-none focus:bg-white focus:border-[#351078] transition-colors"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => onSearchChange && onSearchChange('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#5B4B7A] hover:text-[#230852]"
                aria-label="Clear search"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </form>

          {/* Daily / Weekly / Monthly Selector */}
          <div className="inline-flex bg-[#F2ECFF] p-1 rounded-xl border border-[#D8C5FF]">
            {[
              { id: 'daily', label: 'Daily' },
              { id: 'weekly', label: 'Weekly' },
              { id: 'monthly', label: 'Monthly' },
            ].map((rng) => {
              const active = dateRange === rng.id;
              return (
                <button
                  key={rng.id}
                  type="button"
                  onClick={() => onDateRangeChange && onDateRangeChange(rng.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                    active
                      ? 'bg-[#351078] text-white shadow-xs'
                      : 'text-[#5B4B7A] hover:text-[#351078]'
                  }`}
                >
                  {rng.label}
                </button>
              );
            })}
          </div>

          {/* My Food Cart Button */}
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('cart')}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#EEF8FC] hover:bg-[#ADD8E6]/40 text-[#230852] text-xs font-bold border border-[#ADD8E6] transition-colors"
            title="Open My Food Cart"
          >
            <ShoppingCart className="w-4 h-4 text-[#351078]" />
            <span className="hidden md:inline">Food Cart</span>
            <span className="px-1.5 py-0.5 rounded-full bg-[#C6FF00] text-[#230852] text-[10px] font-extrabold">
              {cartCount}
            </span>
          </button>

          {/* Log Meal / Expense CTA */}
          <button
            type="button"
            onClick={onOpenLogModal}
            className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4 text-[#C6FF00]" />
            <span>Log Meal</span>
          </button>

          {/* Notification Icon */}
          <div className="relative" ref={notifRef}>
            <button
              type="button"
              onClick={() => setNotifOpen((o) => !o)}
              className="relative p-2 rounded-xl bg-[#F2ECFF] hover:bg-[#E5DAFB] border border-[#D8C5FF] text-[#351078] transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-4 h-4" />
              {notifications.length > 0 && (
                <span
                  className={`absolute -top-1 -right-1 w-4 h-4 rounded-full text-[9px] font-extrabold flex items-center justify-center ${
                    warningCount > 0 ? 'bg-[#F59E0B] text-white' : 'bg-[#C6FF00] text-[#230852]'
                  }`}
                >
                  {notifications.length}
                </span>
              )}
            </button>

            {notifOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl border border-[#D8C5FF] shadow-xl p-3 z-50 space-y-2">
                <div className="flex items-center justify-between pb-2 border-b border-[#F2ECFF]">
                  <span className="text-xs font-extrabold text-[#351078] uppercase tracking-wider">
                    Notifications
                  </span>
                  <span className="text-[11px] font-semibold text-[#5B4B7A]">Live Status</span>
                </div>
                {notifications.length === 0 ? (
                  <p className="text-xs text-[#5B4B7A] py-4 text-center">No notifications yet.</p>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {notifications.map((n) => (
                      <div
                        key={n.id}
                        className="p-2.5 rounded-xl bg-[#F2ECFF]/60 border border-[#D8C5FF] flex items-start gap-2.5"
                      >
                        {n.severity === 'warning' ? (
                          <AlertTriangle className="w-4 h-4 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                        ) : n.severity === 'success' ? (
                          <CheckCircle2 className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
                        ) : (
                          <Info className="w-4 h-4 text-[#351078] flex-shrink-0 mt-0.5" />
                        )}
                        <div>
                          <p className="text-xs font-bold text-[#230852]">{n.title}</p>
                          <p className="text-[11px] text-[#5B4B7A] leading-snug mt-0.5">{n.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Profile Avatar Chip */}
          <button
            type="button"
            onClick={() => (isAuthenticated ? onNavigate && onNavigate('profile') : onOpenAuth && onOpenAuth())}
            className="flex items-center gap-2 pl-1.5 pr-3 py-1 rounded-xl bg-[#F2ECFF] hover:bg-[#E5DAFB] border border-[#D8C5FF] transition-colors"
            title={isAuthenticated ? 'Open User Profile' : 'Sign In / Register'}
          >
            <div className="w-7 h-7 rounded-lg bg-[#351078] text-[#C6FF00] font-bold text-xs flex items-center justify-center">
              {displayName.charAt(0).toUpperCase()}
            </div>
            <span className="text-xs font-bold text-[#351078] hidden md:inline max-w-[96px] truncate">
              {isAuthenticated ? displayName : 'Sign In'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopHeader;
