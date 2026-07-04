import React, { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { Sidebar } from './Sidebar';
import { Menu, X, Sparkles } from 'lucide-react';

export const Layout: React.FC = () => {
  const { user, loading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-dark-950 font-sans">
        <div className="relative flex flex-col items-center">
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-purple-500 border-t-transparent"></div>
          <span className="mt-4 text-sm font-mono text-purple-400">Loading StudyMind...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gradient-mesh font-sans text-gray-200">
      {/* Background Orbs */}
      <div className="absolute top-[-20%] left-[-20%] h-[70vh] w-[70vw] rounded-full bg-purple-900/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-20%] h-[70vh] w-[70vw] rounded-full bg-teal-900/10 blur-[120px] pointer-events-none" />

      {/* Desktop Sidebar */}
      <aside className="hidden md:block w-64 h-full shrink-0">
        <Sidebar />
      </aside>

      {/* Mobile Sidebar overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <aside className="relative w-64 h-full z-10 animate-slide-in-left">
            <Sidebar onClose={() => setMobileMenuOpen(false)} />
          </aside>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Header / Top bar */}
        <header className="h-16 shrink-0 flex items-center justify-between px-6 border-b border-glass-border bg-dark-900/20 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 rounded-xl hover:bg-glass-white text-gray-400 hover:text-white transition-colors"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-400 animate-float" />
              <span className="font-semibold text-white tracking-wide">StudyMind Workspace</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-xs text-gray-400">Streak Status</span>
              <span className="text-xs font-mono text-teal-400 font-bold">🎯 active</span>
            </div>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
