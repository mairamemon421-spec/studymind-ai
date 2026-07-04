import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar,
  LineChart,
  Line,
  CartesianGrid
} from 'recharts';
import { BarChart3, TrendingUp, Sparkles, AlertTriangle, Compass, Award } from 'lucide-react';
import toast from 'react-hot-toast';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const res = await api.progress.get();
        setData(res);
      } catch (err: any) {
        toast.error('Failed to load analytics: ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-purple-500 border-t-transparent" />
      </div>
    );
  }

  // Prep charts data
  const masteryData = Object.entries(data?.readiness_scores || {}).map(([name, val]: any) => ({
    subject: name,
    score: Math.round(val * 100),
  }));

  // Week study hours timeline mock
  const studyHoursData = [
    { day: 'Mon', hours: Math.min(data?.hours_studied_week || 4, 1.5) },
    { day: 'Tue', hours: Math.min(data?.hours_studied_week || 4, 2.0) },
    { day: 'Wed', hours: Math.max(0, (data?.hours_studied_week || 0) - 3.5) },
    { day: 'Thu', hours: 0 },
    { day: 'Fri', hours: 0 },
    { day: 'Sat', hours: 0 },
    { day: 'Sun', hours: 0 },
  ];

  // Quiz score timeline mock
  const quizProgressData = [
    { test: 'Quiz 1', score: 60 },
    { test: 'Quiz 2', score: 70 },
    { test: 'Quiz 3', score: 85 },
    { test: 'Quiz 4', score: 90 },
  ];

  // Identify weak areas (less than 60% readiness)
  const weakAreas = Object.entries(data?.readiness_scores || {})
    .filter(([_, val]: any) => val < 0.6)
    .map(([name]) => name);

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="border-b border-glass-border pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-purple-400" />
          <span>Analytics Dashboard</span>
        </h2>
        <p className="text-xs text-gray-400 mt-1">
          Deep-dive analysis of your topic mastery scores, study timeline logs, and quiz results.
        </p>
      </div>

      {masteryData.length === 0 ? (
        <div className="glass-card p-12 text-center text-gray-500 max-w-lg mx-auto">
          <Compass className="h-10 w-10 mx-auto text-gray-600 mb-2" />
          <h4 className="text-white font-bold text-base mb-1">No Analytics Available</h4>
          <p className="text-xs">
            Add study subjects and schedule session plans to feed indicators to the Analytics engine.
          </p>
        </div>
      ) : (
        <>
          {/* Top summary boxes */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card p-5 flex items-start gap-4">
              <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-2xl text-purple-400 shrink-0">
                <TrendingUp className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider block">Average Mastery</span>
                <h4 className="text-xl font-bold text-white">
                  {Math.round((data?.overall_readiness || 0) * 100)}%
                </h4>
                <p className="text-[10px] text-gray-400">Aggregated across all subjects</p>
              </div>
            </div>

            <div className="glass-card p-5 flex items-start gap-4">
              <div className="p-3 bg-teal-500/10 border border-teal-500/20 rounded-2xl text-teal-400 shrink-0">
                <Award className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider block">Total Completed</span>
                <h4 className="text-xl font-bold text-white">
                  {data?.total_sessions_completed || 0} Slots
                </h4>
                <p className="text-[10px] text-gray-400">Study sessions logged done</p>
              </div>
            </div>

            {/* Weak Areas Alerts */}
            <div className="glass-card p-5 flex items-start gap-4 border-l-2 border-l-amber-500/60">
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-2xl text-amber-400 shrink-0">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <div className="space-y-1 flex-1">
                <span className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider block">Alert Zones</span>
                <h4 className="text-xs font-bold text-white">
                  {weakAreas.length > 0 ? `${weakAreas.length} Subject(s) need attention` : 'All subjects look solid!'}
                </h4>
                <p className="text-[10px] text-gray-400 truncate max-w-[200px]">
                  {weakAreas.length > 0 ? weakAreas.join(', ') : 'Ready score above 60%'}
                </p>
              </div>
            </div>
          </div>

          {/* Charts grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Subject Readiness Radar Chart */}
            <div className="glass-card p-6 h-[340px] flex flex-col">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-1.5">
                <Compass className="h-4.5 w-4.5 text-purple-400" />
                <span>Subject Readiness Profile</span>
              </h3>
              <div className="flex-1 w-full text-xs min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="55%" cy="50%" outerRadius="80%" data={masteryData}>
                    <PolarGrid stroke="#242450" />
                    <PolarAngleAxis dataKey="subject" stroke="#a970ff" fontSize={10} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#242450" fontSize={8} />
                    <Radar name="Readiness" dataKey="score" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.2} />
                    <Tooltip contentStyle={{ backgroundColor: '#0a0a1a', borderColor: '#242450', borderRadius: '8px' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Weekly Study Hours Bar Chart */}
            <div className="glass-card p-6 h-[340px] flex flex-col">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-1.5">
                <TrendingUp className="h-4.5 w-4.5 text-purple-400" />
                <span>Study Activity (This Week)</span>
              </h3>
              <div className="flex-1 w-full text-xs min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={studyHoursData}>
                    <XAxis dataKey="day" stroke="#a970ff" fontSize={10} />
                    <YAxis stroke="#a970ff" fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#0a0a1a', borderColor: '#242450', borderRadius: '8px' }} />
                    <Bar dataKey="hours" fill="url(#barColors)" radius={[4, 4, 0, 0]} />
                    <defs>
                      <linearGradient id="barColors" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#9047ff" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.2}/>
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Quiz performance trend line */}
            <div className="glass-card p-6 h-[340px] flex flex-col lg:col-span-2">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-1.5">
                <Sparkles className="h-4.5 w-4.5 text-purple-400" />
                <span>Quiz Scores Progression</span>
              </h3>
              <div className="flex-1 w-full text-xs min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={quizProgressData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#242450" />
                    <XAxis dataKey="test" stroke="#a970ff" fontSize={10} />
                    <YAxis stroke="#a970ff" fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#0a0a1a', borderColor: '#242450', borderRadius: '8px' }} />
                    <Line type="monotone" dataKey="score" stroke="#14b8a6" strokeWidth={2} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
