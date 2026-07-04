import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import {
  LayoutDashboard,
  BookOpen,
  CalendarDays,
  MessageSquare,
  FileQuestion,
  BarChart3,
  Terminal,
  LogOut,
  Database
} from 'lucide-react';

interface SidebarProps {
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Subjects & Exams', path: '/subjects', icon: BookOpen },
    { name: 'Study Plan', path: '/plan', icon: CalendarDays },
    { name: 'AI Tutor', path: '/tutor', icon: MessageSquare },
    { name: 'Quizzes', path: '/quiz', icon: FileQuestion },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Agent Logs', path: '/logs', icon: Terminal },
  ];

  const handleLogout = () => {
    logout();
    if (onClose) onClose();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-full bg-dark-900/40 border-r border-glass-border backdrop-blur-xl p-4">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-2 py-4 mb-6">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-purple-600 to-teal-500 flex items-center justify-center font-bold text-white shadow-purple-glow">
          SM
        </div>
        <div>
          <h1 className="font-bold text-lg text-white leading-tight">StudyMind AI</h1>
          <span className="text-xs text-purple-400 font-mono">Multi-Agent Tutor</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? 'bg-purple-500/20 text-purple-200 border-l-2 border-purple-500 shadow-purple-glow/10'
                    : 'text-gray-400 hover:bg-glass-white hover:text-white'
                }`
              }
            >
              <Icon className="h-5 w-5" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="border-t border-glass-border pt-4 mt-auto">
        <div className="flex items-center justify-between gap-2 px-2">
          <div className="flex flex-col">
            <span className="text-sm font-medium text-white truncate max-w-[120px]">
              {user?.full_name || 'Student'}
            </span>
            <span className="text-xs text-gray-500 truncate max-w-[120px]">
              {user?.email}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="p-2 rounded-xl text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
            title="Log Out"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
