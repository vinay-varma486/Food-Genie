import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './AuthContext';
import {
  Sparkles, ChevronDown, User, LogOut, LogIn,
  TrendingUp, TrendingDown, Scale, Wallet, MapPin, Bookmark, Settings, Menu, X
} from 'lucide-react';

export const Navbar = ({
  currentPage = 'home',
  onNavigate,
  onOpenAuth,
}) => {
  const { displayName, isAuthenticated, logout } = useAuth();
  const [moreOpen, setMoreOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const moreRef = useRef(null);

  useEffect(() => {
    const handleOutside = (e) => {
      if (moreRef.current && !moreRef.current.contains(e.target)) {
        setMoreOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  const primaryLinks = [
    { id: 'home', label: 'Home' },
    { id: 'explore', label: 'Explore Foods' },
    { id: 'about', label: 'About' },
  ];

  const moreItems = [
    { id: 'goal-gain', label: 'Weight Gain Planner', desc: 'Healthy calorie & protein surplus', icon: TrendingUp },
    { id: 'goal-loss', label: 'Weight Loss Planner', desc: 'Filling, balanced deficit plan', icon: TrendingDown },
    { id: 'goal-maintain', label: 'Weight Maintenance Planner', desc: 'Steady daily nutrition balance', icon: Scale },
    { id: 'budget', label: 'Budget Planner', desc: 'Daily, weekly & monthly ₹ plans', icon: Wallet },
    { id: 'doctors', label: 'Nearby Doctors', desc: 'Verified clinics & specialists', icon: MapPin },
    { id: 'saved', label: 'My Saved Plans', desc: 'Saved plans, foods & chats', icon: Bookmark },
    { id: 'profile', label: 'Profile and Settings', desc: 'Account, goals & preferences', icon: Settings },
  ];

  const isMoreActive = currentPage === 'more' || moreItems.some((m) => m.id === currentPage);

  const navigateTo = (pageId) => {
    setMoreOpen(false);
    setMobileOpen(false);
    if (onNavigate) onNavigate(pageId);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-lavender-border shadow-xs">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">

        {/* Brand Logo */}
        <button
          type="button"
          onClick={() => navigateTo('home')}
          className="flex items-center gap-2.5 text-left focus:outline-none"
        >
          <div className="w-9 h-9 rounded-xl bg-royal flex items-center justify-center shadow-xs">
            <Sparkles className="w-5 h-5 text-lime-electric" />
          </div>
          <div>
            <span className="font-display font-extrabold text-lg tracking-tight text-royal">
              Food<span className="bg-lime-electric text-royal-deep px-1.5 py-0.5 rounded-md ml-0.5">Genie</span>
            </span>
          </div>
        </button>

        {/* Main 4 Navigation Items: Home, Explore Foods, About, More */}
        <nav className="hidden md:flex items-center gap-1 bg-lavender-mist/70 p-1 rounded-full border border-lavender-border">
          {primaryLinks.map((link) => {
            const active = currentPage === link.id;
            return (
              <button
                key={link.id}
                type="button"
                onClick={() => navigateTo(link.id)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold transition-colors ${
                  active
                    ? 'bg-royal text-white shadow-xs'
                    : 'text-royal/80 hover:text-royal hover:bg-white/70'
                }`}
              >
                {link.label}
              </button>
            );
          })}

          {/* More Dropdown */}
          <div className="relative" ref={moreRef}>
            <button
              type="button"
              onClick={() => setMoreOpen((o) => !o)}
              aria-expanded={moreOpen}
              className={`px-4 py-1.5 rounded-full text-xs font-bold flex items-center gap-1 transition-colors ${
                isMoreActive || moreOpen
                  ? 'bg-royal text-white shadow-xs'
                  : 'text-royal/80 hover:text-royal hover:bg-white/70'
              }`}
            >
              <span>More</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${moreOpen ? 'rotate-180' : ''}`} />
            </button>

            {moreOpen && (
              <div className="absolute right-0 mt-2.5 w-72 bg-white rounded-2xl shadow-card border border-lavender-border py-2 z-50">
                <div className="px-4 py-1.5 border-b border-lavender-mist flex items-center justify-between">
                  <p className="text-[10px] font-extrabold uppercase tracking-wider text-royal/50">
                    Planners &amp; Tools
                  </p>
                  <button
                    type="button"
                    onClick={() => navigateTo('more')}
                    className="text-[10px] font-bold text-royal hover:underline"
                  >
                    View All
                  </button>
                </div>
                {moreItems.map((item) => {
                  const Icon = item.icon;
                  const active = currentPage === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => navigateTo(item.id)}
                      className={`w-full text-left px-4 py-2.5 flex items-center gap-3 transition-colors ${
                        active ? 'bg-lavender-mist text-royal' : 'hover:bg-lavender-light text-royal-deep'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        active ? 'bg-royal text-lime-electric' : 'bg-lavender-mist text-royal'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-bold leading-tight">{item.label}</p>
                        <p className="text-[11px] text-royal/60 truncate">{item.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </nav>

        {/* Right: Auth / Account Actions */}
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <button
                type="button"
                onClick={() => navigateTo('profile')}
                className="flex items-center gap-2 pl-1.5 pr-3 py-1 rounded-full bg-lavender-mist hover:bg-lavender-dark border border-lavender-border transition-colors"
                title="Profile and Settings"
              >
                <div className="w-7 h-7 rounded-full bg-royal text-lime-electric flex items-center justify-center font-bold text-xs">
                  {displayName.charAt(0).toUpperCase()}
                </div>
                <span className="text-xs font-bold text-royal hidden sm:inline max-w-[110px] truncate">
                  {displayName}
                </span>
              </button>
              <button
                type="button"
                onClick={logout}
                className="hidden sm:flex items-center gap-1 px-3 py-1.5 rounded-full border border-lavender-border text-xs font-bold text-royal/75 hover:text-red-700 hover:bg-red-50 transition-colors"
                title="Logout"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-royal hover:bg-royal-light text-white text-xs font-bold shadow-xs transition-colors"
            >
              <LogIn className="w-3.5 h-3.5 text-lime-electric" />
              <span>Sign In</span>
            </button>
          )}

          {/* Mobile Menu Toggle */}
          <button
            type="button"
            onClick={() => setMobileOpen((m) => !m)}
            className="md:hidden p-2 rounded-xl border border-lavender-border text-royal hover:bg-lavender-mist"
            aria-label="Toggle Menu"
          >
            {mobileOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileOpen && (
        <div className="md:hidden border-t border-lavender-border bg-white px-4 py-3 space-y-2">
          <div className="grid grid-cols-4 gap-1.5">
            {[...primaryLinks, { id: 'more', label: 'More' }].map((link) => (
              <button
                key={link.id}
                type="button"
                onClick={() => navigateTo(link.id)}
                className={`py-2 px-1.5 rounded-xl text-xs font-bold text-center truncate ${
                  currentPage === link.id
                    ? 'bg-royal text-white'
                    : 'bg-lavender-mist/70 text-royal'
                }`}
              >
                {link.label}
              </button>
            ))}
          </div>

          <div className="pt-2 border-t border-lavender-mist">
            <p className="text-[10px] font-extrabold uppercase tracking-wider text-royal/50 mb-1.5">
              More
            </p>
            <div className="grid grid-cols-1 gap-1">
              {moreItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => navigateTo(item.id)}
                    className={`w-full text-left px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-2.5 ${
                      currentPage === item.id ? 'bg-royal text-white' : 'hover:bg-lavender-mist text-royal'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
              {isAuthenticated && (
                <button
                  type="button"
                  onClick={() => { setMobileOpen(false); logout(); }}
                  className="w-full text-left px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-2.5 text-red-700 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
