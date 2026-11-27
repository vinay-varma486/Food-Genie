import React from 'react';
import {
  LayoutDashboard,
  Wallet,
  PieChart,
  CalendarDays,
  LayoutGrid,
  Sparkles,
  ShoppingCart,
  ShoppingBag,
  FileBarChart2,
  Settings,
  User,
  Stethoscope,
  LogOut,
  LogIn,
  X,
  Info,
} from 'lucide-react';
import { useAuth } from './AuthContext';

export const SIDEBAR_NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'cart', label: 'My Food Cart', icon: ShoppingCart },
  { id: 'budget', label: 'Budget Planner', icon: Wallet },
  { id: 'analytics', label: 'Nutrition Analytics', icon: PieChart },
  { id: 'meal-planner', label: 'Meal Planner', icon: CalendarDays },
  { id: 'categories', label: 'Food Categories', icon: LayoutGrid },
  { id: 'recommendations', label: 'Food Recommendations', icon: Sparkles },
  { id: 'shopping-list', label: 'Shopping List', icon: ShoppingBag },
  { id: 'reports', label: 'Reports', icon: FileBarChart2 },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'profile', label: 'User Profile', icon: User },
];

export const Sidebar = ({
  currentPage = 'dashboard',
  onNavigate,
  onOpenAuth,
  mobileOpen = false,
  onCloseMobile,
  cartCount = 0,
}) => {
  const { isAuthenticated, displayName, logout } = useAuth();

  const handleSelect = (id) => {
    if (onNavigate) onNavigate(id);
    if (onCloseMobile) onCloseMobile();
  };

  const isActive = (id) => {
    if (currentPage === id) return true;
    if (id === 'dashboard' && currentPage === 'home') return true;
    if (id === 'meal-planner' && ['goal-gain', 'goal-loss', 'goal-maintain'].includes(currentPage)) return true;
    if (id === 'categories' && currentPage === 'explore') return true;
    return false;
  };

  const navContent = (
    <div className="flex flex-col h-full bg-white border-r border-[#D8C5FF] select-none">
      {/* Brand Logo */}
      <div className="h-16 px-5 flex items-center justify-between border-b border-[#F2ECFF] flex-shrink-0">
        <button
          type="button"
          onClick={() => handleSelect('dashboard')}
          className="flex items-center gap-3 text-left focus:outline-none"
        >
          <div className="w-9 h-9 rounded-xl bg-[#351078] flex items-center justify-center shadow-sm">
            <Sparkles className="w-5 h-5 text-[#C6FF00]" />
          </div>
          <div>
            <span className="font-display font-extrabold text-lg tracking-tight text-[#351078] block leading-none">
              Food<span className="bg-[#C6FF00] text-[#230852] px-1.5 py-0.5 rounded-md ml-0.5">Genie</span>
            </span>
            <span className="text-[10px] font-semibold text-[#5B4B7A] tracking-wide">
              Nutrition &amp; Meal Platform
            </span>
          </div>
        </button>

        {onCloseMobile && (
          <button
            type="button"
            onClick={onCloseMobile}
            className="lg:hidden p-1.5 rounded-lg text-[#5B4B7A] hover:bg-[#F2ECFF] hover:text-[#351078]"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <p className="px-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-[#5B4B7A]">
          Workspace
        </p>
        {SIDEBAR_NAV_ITEMS.slice(0, 9).map((item) => {
          const Icon = item.icon;
          const active = isActive(item.id);
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSelect(item.id)}
              className={`w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 ${
                active
                  ? 'bg-[#351078] text-white shadow-sm'
                  : 'text-[#5B4B7A] hover:bg-[#F2ECFF] hover:text-[#351078]'
              }`}
            >
              <span className="flex items-center gap-3 min-w-0">
                <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-[#C6FF00]' : 'text-[#5B4B7A]'}`} />
                <span className="truncate">{item.label}</span>
              </span>
              {item.id === 'cart' && cartCount > 0 && (
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                    active ? 'bg-[#C6FF00] text-[#230852]' : 'bg-[#EEF8FC] text-[#351078] border border-[#ADD8E6]'
                  }`}
                >
                  {cartCount}
                </span>
              )}
            </button>
          );
        })}

        <div className="pt-4 pb-1">
          <p className="px-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-[#5B4B7A]">
            Care &amp; Account
          </p>
        </div>

        <button
          type="button"
          onClick={() => handleSelect('doctors')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 ${
            currentPage === 'doctors'
              ? 'bg-[#351078] text-white shadow-sm'
              : 'text-[#5B4B7A] hover:bg-[#F2ECFF] hover:text-[#351078]'
          }`}
        >
          <Stethoscope className={`w-4 h-4 flex-shrink-0 ${currentPage === 'doctors' ? 'text-[#C6FF00]' : ''}`} />
          <span className="truncate">Find Doctors</span>
        </button>

        {SIDEBAR_NAV_ITEMS.slice(9).map((item) => {
          const Icon = item.icon;
          const active = isActive(item.id);
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSelect(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 ${
                active
                  ? 'bg-[#351078] text-white shadow-sm'
                  : 'text-[#5B4B7A] hover:bg-[#F2ECFF] hover:text-[#351078]'
              }`}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-[#C6FF00]' : 'text-[#5B4B7A]'}`} />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}

        <button
          type="button"
          onClick={() => handleSelect('about')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 ${
            currentPage === 'about'
              ? 'bg-[#351078] text-white shadow-sm'
              : 'text-[#5B4B7A] hover:bg-[#F2ECFF] hover:text-[#351078]'
          }`}
        >
          <Info className={`w-4 h-4 flex-shrink-0 ${currentPage === 'about' ? 'text-[#C6FF00]' : ''}`} />
          <span className="truncate">About &amp; Data Sources</span>
        </button>
      </nav>

      {/* Bottom Auth / Account Footer */}
      <div className="p-3 border-t border-[#F2ECFF] bg-[#FAF7FF]">
        {isAuthenticated ? (
          <div className="flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => handleSelect('profile')}
              className="flex items-center gap-2.5 min-w-0 text-left hover:opacity-85"
            >
              <div className="w-8 h-8 rounded-full bg-[#351078] text-[#C6FF00] font-bold text-xs flex items-center justify-center flex-shrink-0">
                {displayName.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-bold text-[#230852] truncate">{displayName}</p>
                <p className="text-[10px] text-[#16A34A] font-semibold">Verified Account</p>
              </div>
            </button>
            <button
              type="button"
              onClick={logout}
              className="p-2 rounded-lg text-[#5B4B7A] hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => {
              if (onCloseMobile) onCloseMobile();
              if (onOpenAuth) onOpenAuth();
            }}
            className="w-full py-2.5 px-3 rounded-xl bg-[#351078] hover:bg-[#4C18AB] text-white text-xs font-bold flex items-center justify-center gap-2 transition-colors"
          >
            <LogIn className="w-4 h-4 text-[#C6FF00]" />
            <span>Sign In / Register</span>
          </button>
        )}
      </div>
    </div>
  );

  return (
    <>
      <aside className="hidden lg:block w-64 flex-shrink-0 sticky top-0 h-screen z-30">
        {navContent}
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-[#230852]/45 backdrop-blur-xs"
            onClick={onCloseMobile}
          />
          <div className="relative w-72 max-w-[85vw] h-full z-10 shadow-xl">
            {navContent}
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
