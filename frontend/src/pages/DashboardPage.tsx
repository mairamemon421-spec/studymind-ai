import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { 
  Trophy, 
  BookOpen, 
  Hourglass, 
  Compass, 
  ChevronRight, 
  CalendarDays, 
  AlertCircle, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import toast from 'react-hot-toast';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchProgress = async () => {
    try {
      setLoading(true);
      const res = await api.progress.get();
      setData(res);
    } catch (err: any) {
      toast.error('Failed to load study metrics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProgress();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-purple-500 border-t-transparent"></div>
      </div>
    );
  }

  const statCards = [
    {
      name: 'Current Streak',
      value: `${data?.streak_days || 0} Days`,
      desc: 'Days studied back-to-back',
      icon: Trophy,
      color: 'from-amber-500 to-yellow-400',
      badge: data?.streak_days > 0 ? '🔥 On Fire' : '🏁 Get Started',
    },
    {
      name: 'Study Readiness',
      value: `${Math.round((data?.overall_readiness || 0) * 100)}%`,
      desc: 'Based on mastery & quizzes',
      icon: Compass,
      color: 'from-purple-600 to-purple-400',
      badge: '🎯 Current Score',
    },
    {
      name: 'Sessions Today',
      value: `${data?.sessions_today || 0} Done`,
      desc: 'Planned study slots for today',
      icon: BookOpen,
      color: 'from-teal-500 to-emerald-400',
      badge: '📈 Daily Goal',
    },
    {
      name: 'Study Hours (Week)',
      value: `${data?.hours_studied_week || 0} hrs`,
      desc: 'Accumulated this week',
      icon: Hourglass,
      color: 'from-blue-600 to-cyan-400',
      badge: '🕒 Target',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome banner */}
      <div className="glass-card p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 overflow-hidden relative">
        <div className="absolute right-0 top-0 h-40 w-40 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="space-y-2">
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Hello, ready to master your topics? 🚀
          </h2>
          <p className="text-gray-400 max-w-xl text-sm">
            StudyMind AI coordinate priority ranking, schedules, chat tutors, and quiz models. Rank, generate study planner, chat concepts, test with quiz!
          </p>
        </div>
        <div className="flex gap-3 shrink-0">
          <Link to="/plan" className="btn-primary flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            <span>Generate Study Plan</span>
          </Link>
        </div>
      </div>

      {/* Grid of stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="glass-card p-6 flex flex-col justify-between h-40">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs text-gray-500 font-semibold uppercase tracking-wider">{card.name}</span>
                  <h3 className="text-2xl font-bold text-white mt-1">{card.value}</h3>
                </div>
                <div className={`p-2 rounded-xl bg-gradient-to-br ${card.color} text-white shadow-md`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <div className="flex items-center justify-between border-t border-glass-border pt-3">
                <span className="text-xs text-gray-400 truncate max-w-[130px]">{card.desc}</span>
                <span className="text-[10px] font-semibold text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded-full border border-teal-500/10 shrink-0">
                  {card.badge}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 columns: Subject Mastery and quick actions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-white">Subject Mastery</h3>
              <Link to="/subjects" className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1">
                <span>Manage Subjects</span>
                <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            {Object.keys(data?.readiness_scores || {}).length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="h-8 w-8 mx-auto text-gray-600 mb-2" />
                <p className="text-sm">No subjects found. Create subjects to analyze mastery.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {Object.entries(data.readiness_scores).map(([name, val]: any, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-gray-300">{name}</span>
                      <span className="font-mono text-teal-400 font-semibold">{Math.round(val * 100)}% Readiness</span>
                    </div>
                    <div className="h-2 w-full bg-dark-800 rounded-full overflow-hidden border border-glass-border">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-500 to-teal-400 transition-all duration-500"
                        style={{ width: `${Math.round(val * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick AI Assist Card */}
          <div className="glass-card p-6 bg-gradient-to-br from-dark-900 via-dark-800 to-purple-950/20 border border-purple-500/20">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-2xl text-purple-400 animate-float">
                <Sparkles className="h-6 w-6" />
              </div>
              <div className="space-y-2 flex-1">
                <h4 className="text-md font-bold text-white">Ask StudyMind AI Tutor</h4>
                <p className="text-xs text-gray-400">
                  Concept questions? Analogy clarifications? Tap into tutor chat right away!
                </p>
                <Link to="/tutor" className="inline-flex items-center gap-1.5 text-xs text-purple-400 font-semibold hover:gap-2.5 transition-all">
                  <span>Chat with Tutor</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right 1 column: Upcoming Exams */}
        <div className="glass-card p-6 flex flex-col h-full">
          <div className="flex items-center justify-between mb-6 shrink-0">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-purple-400" />
              <span>Upcoming Exams</span>
            </h3>
            <Link to="/subjects" className="text-xs text-purple-400 hover:text-purple-300">
              <span>Add</span>
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 max-h-[300px] pr-2">
            {!data?.upcoming_exams || data.upcoming_exams.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <p className="text-xs">No upcoming exams. Add exams in the Subjects tab to schedule preparation.</p>
              </div>
            ) : (
              data.upcoming_exams.map((exam: any, idx: number) => {
                const diffDays = Math.ceil((new Date(exam.exam_date).getTime() - new Date().getTime()) / (1000 * 3600 * 24));
                return (
                  <div key={idx} className="p-3.5 rounded-xl bg-glass-white border border-glass-border flex justify-between items-center gap-3">
                    <div className="min-w-0">
                      <h4 className="text-sm font-semibold text-white truncate">{exam.title}</h4>
                      <span className="text-[10px] text-gray-500 block mt-0.5">
                        Date: {new Date(exam.exam_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0 ${
                      diffDays <= 3 
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {diffDays <= 0 ? 'Today' : `${diffDays} days left`}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
