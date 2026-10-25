import React, { useState, useRef, useEffect } from 'react'

export function Header({ currentScreen, onNavigate, onBack }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <header className="bg-white h-[54px] px-4 flex items-center justify-between border-b border-gray-200 flex-shrink-0 relative z-50">
      <div className="flex items-center gap-3">
        {/* Hamburger Menu Trigger */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="w-[36px] h-[36px] flex items-center justify-center rounded-md hover:bg-slate-100 text-slate-800 text-[18px] cursor-pointer transition-colors"
            title="Navigation Menu"
          >
            ☰
          </button>

          {/* Hamburger Dropdown / Drawer */}
          {menuOpen && (
            <div className="absolute top-[44px] left-0 w-[210px] bg-white border border-slate-200 rounded-xl shadow-xl py-2 flex flex-col z-[100]">
              <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                Navigation Menu
              </div>
              <button
                onClick={() => { onNavigate('home'); setMenuOpen(false); }}
                className={`w-full text-left px-3 py-2 text-[13px] font-medium flex items-center gap-2 cursor-pointer transition-colors ${
                  currentScreen === 'home' ? 'bg-slate-100 text-slate-900 font-semibold' : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                Facilities
              </button>
              <button
                onClick={() => { onNavigate('route'); setMenuOpen(false); }}
                className={`w-full text-left px-3 py-2 text-[13px] font-medium flex items-center gap-2 cursor-pointer transition-colors ${
                  currentScreen === 'route' ? 'bg-slate-100 text-slate-900 font-semibold' : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                Route Planner
              </button>
              <button
                onClick={() => { onNavigate('chat'); setMenuOpen(false); }}
                className={`w-full text-left px-3 py-2 text-[13px] font-medium flex items-center gap-2 cursor-pointer transition-colors ${
                  currentScreen === 'chat' ? 'bg-slate-100 text-slate-900 font-semibold' : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                CampusFlow AI
              </button>
              <button
                onClick={() => { onNavigate('profile'); setMenuOpen(false); }}
                className={`w-full text-left px-3 py-2 text-[13px] font-medium flex items-center gap-2 cursor-pointer transition-colors ${
                  currentScreen === 'profile' ? 'bg-slate-100 text-slate-900 font-semibold' : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                Profile
              </button>
            </div>
          )}
        </div>

        {/* Back Button (if not on home) */}
        {currentScreen !== 'home' && (
          <button
            onClick={onBack}
            className="h-[32px] px-2 flex items-center gap-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 text-[12px] font-medium transition-colors cursor-pointer"
            title="Go back"
          >
            ← Back
          </button>
        )}
      </div>

      {/* Title */}
      <div className="flex items-center">
        <span className="text-[15px] font-bold tracking-tight text-slate-900">
          {currentScreen === 'home' && 'CampusFlow'}
          {currentScreen === 'detail' && 'Facility Details'}
          {currentScreen === 'route' && 'Route Planner'}
          {currentScreen === 'chat' && 'CampusFlow AI'}
          {currentScreen === 'profile' && 'Student Profile'}
        </span>
      </div>

      {/* Right badge / indicator */}
      <div className="flex items-center">
        <span className="text-[11px] font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
          {currentScreen === 'home' && 'Live'}
          {currentScreen === 'detail' && 'Status'}
          {currentScreen === 'route' && 'Multi-Agent'}
          {currentScreen === 'chat' && 'Active'}
          {currentScreen === 'profile' && 'Account'}
        </span>
      </div>
    </header>
  )
}

export function BottomNav({ currentScreen, onNavigate }) {
  return (
    <nav className="h-[56px] bg-white border-t border-gray-200 flex justify-around items-center flex-shrink-0">
      <button
        onClick={() => onNavigate('home')}
        className={`nav-item flex flex-col items-center justify-center gap-[3px] min-w-[44px] min-h-[44px] bg-transparent border-none cursor-pointer text-[12px] font-medium ${
          currentScreen === 'home' ? 'text-brand-primary font-semibold' : 'text-gray-500'
        }`}
      >
        <span>Facilities</span>
      </button>
      <button
        onClick={() => onNavigate('route')}
        className={`nav-item flex flex-col items-center justify-center gap-[3px] min-w-[44px] min-h-[44px] bg-transparent border-none cursor-pointer text-[12px] font-medium ${
          currentScreen === 'route' ? 'text-brand-primary font-semibold' : 'text-gray-500'
        }`}
      >
        <span>Route</span>
      </button>
      <button
        onClick={() => onNavigate('chat')}
        className={`nav-item flex flex-col items-center justify-center gap-[3px] min-w-[44px] min-h-[44px] bg-transparent border-none cursor-pointer text-[12px] font-medium ${
          currentScreen === 'chat' ? 'text-brand-primary font-semibold' : 'text-gray-500'
        }`}
      >
        <span>Ask AI</span>
      </button>
    </nav>
  )
}
