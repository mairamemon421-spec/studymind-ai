import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { 
  CalendarDays, 
  Download, 
  Sparkles, 
  CheckCircle, 
  Plus, 
  FileText,
  Clock,
  Compass,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

export const PlanPage: React.FC = () => {
  const [plans, setPlans] = useState<any[]>([]);
  const [activePlan, setActivePlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [weeks, setWeeks] = useState(2);

  // Completion modal state
  const [completingSession, setCompletingSession] = useState<any>(null);
  const [completionNotes, setCompletionNotes] = useState('');

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const res = await api.plans.list();
      setPlans(res);
      if (res.length > 0) {
        setActivePlan(res[0]);
      }
    } catch (err: any) {
      toast.error('Failed to load study plans: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const newPlan = await api.plans.generate({ weeks_ahead: weeks });
      setPlans([newPlan, ...plans]);
      setActivePlan(newPlan);
      toast.success('Study plan generated successfully by Coordinator agent!');
    } catch (err: any) {
      toast.error('Generation failed: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleCompleteSession = async () => {
    if (!completingSession) return;
    try {
      await api.plans.completeSession(activePlan.id, completingSession.id, completionNotes);
      toast.success('Session marked as completed!');
      
      // Update local state
      const updatedSessions = activePlan.sessions.map((s: any) => 
        s.id === completingSession.id ? { ...s, completed: true, notes: completionNotes } : s
      );
      
      const newActive = { ...activePlan, sessions: updatedSessions };
      setActivePlan(newActive);
      setPlans(plans.map((p) => (p.id === activePlan.id ? newActive : p)));

      // Close modal
      setCompletingSession(null);
      setCompletionNotes('');
    } catch (err: any) {
      toast.error('Failed to update session: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-purple-500 border-t-transparent" />
      </div>
    );
  }

  // Sort sessions chronologically
  const sessions = activePlan?.sessions
    ? [...activePlan.sessions].sort((a: any, b: any) => {
        const dateDiff = new Date(a.session_date).getTime() - new Date(b.session_date).getTime();
        if (dateDiff !== 0) return dateDiff;
        return a.start_time.localeCompare(b.start_time);
      })
    : [];

  return (
    <div className="space-y-8 animate-fade-in relative">
      {/* Top action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-glass-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CalendarDays className="h-6 w-6 text-purple-400" />
            <span>AI Study Timetable</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            {activePlan ? `Active Plan: ${activePlan.title}` : 'No active study plans'}
          </p>
        </div>

        {activePlan && (
          <a
            href={api.pdfUrl(activePlan.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary self-start sm:self-center py-2 flex items-center gap-2 text-xs"
          >
            <Download className="h-4 w-4" />
            <span>Download PDF</span>
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Form: Planner configuration / plans history */}
        <div className="space-y-6 lg:col-span-1">
          {/* Generation Configuration */}
          <div className="glass-card p-6">
            <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-400" />
              <span>Generate New Plan</span>
            </h3>
            <form onSubmit={handleGeneratePlan} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Time Horizon (Weeks)</label>
                <select
                  value={weeks}
                  onChange={(e) => setWeeks(parseInt(e.target.value) || 2)}
                  className="input-field bg-dark-800"
                >
                  <option value={1}>1 Week ahead</option>
                  <option value={2}>2 Weeks ahead</option>
                  <option value={3}>3 Weeks ahead</option>
                  <option value={4}>4 Weeks ahead</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={generating}
                className="w-full btn-primary py-2.5 flex items-center justify-center gap-2"
              >
                {generating ? (
                  <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <Sparkles className="h-4.5 w-4.5" />
                    <span>Run Coordinator Agent</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Plan History */}
          <div className="glass-card p-6">
            <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-purple-400" />
              <span>Plan History</span>
            </h3>
            {plans.length === 0 ? (
              <p className="text-xs text-gray-500">No previous plans generated.</p>
            ) : (
              <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                {plans.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setActivePlan(p)}
                    className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                      activePlan?.id === p.id
                        ? 'bg-purple-500/10 text-purple-300 border-purple-500/40 shadow-purple-glow/5'
                        : 'bg-glass-white border-glass-border text-gray-400 hover:bg-glass-hover hover:text-white'
                    }`}
                  >
                    <div className="font-semibold truncate">{p.title}</div>
                    <div className="text-[10px] text-gray-500 mt-1">
                      {p.start_date} to {p.end_date}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Timetable List / Sessions */}
        <div className="lg:col-span-2 space-y-4">
          {!activePlan ? (
            <div className="glass-card p-12 text-center text-gray-500 flex flex-col items-center">
              <Compass className="h-12 w-12 text-gray-600 mb-3" />
              <h4 className="text-white font-bold text-base mb-1">No Study Plan Yet</h4>
              <p className="text-xs max-w-sm mx-auto">
                Trigger the Study Coordinator above to rank subjects and design your structured study timetable automatically.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Coordinator notes */}
              {activePlan.coordinator_notes && (
                <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/10 text-xs text-purple-300 italic">
                  📝 {activePlan.coordinator_notes}
                </div>
              )}

              {/* Sessions list */}
              <div className="space-y-3 overflow-y-auto max-h-[500px] pr-2">
                {sessions.map((sess: any) => {
                  const sdate = new Date(sess.session_date).toLocaleDateString(undefined, {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                  });
                  return (
                    <div
                      key={sess.id}
                      className={`glass-card p-4 flex flex-col sm:flex-row justify-between sm:items-center gap-4 relative overflow-hidden transition-all ${
                        sess.completed ? 'opacity-60 bg-dark-900/10' : ''
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[10px] font-mono bg-purple-500/10 text-purple-300 px-2 py-0.5 rounded-full font-semibold">
                            {sess.subject_name}
                          </span>
                          <span className="text-xs font-semibold text-white">{sdate}</span>
                        </div>
                        <h4 className="text-sm font-semibold text-gray-200 mt-1">{sess.topic}</h4>
                        {sess.notes && (
                          <p className="text-[10px] text-gray-400 bg-dark-800/40 p-1.5 rounded-md border border-glass-border">
                            {sess.notes}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center gap-4 shrink-0 justify-between sm:justify-end">
                        <div className="flex items-center gap-1.5 text-xs text-gray-400">
                          <Clock className="h-4 w-4 text-teal-400" />
                          <span>
                            {sess.start_time} - {sess.end_time} ({sess.duration_minutes}m)
                          </span>
                        </div>

                        {!sess.completed ? (
                          <button
                            onClick={() => setCompletingSession(sess)}
                            className="p-2 rounded-xl text-teal-400 hover:text-teal-300 hover:bg-teal-500/10 transition-colors"
                            title="Mark as completed"
                          >
                            <CheckCircle className="h-5 w-5" />
                          </button>
                        ) : (
                          <span className="text-xs text-teal-400 font-semibold px-2 py-0.5 bg-teal-500/10 rounded-full border border-teal-500/15">
                            ✓ Done
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Completion Modal */}
      {completingSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setCompletingSession(null)} />
          <div className="glass-card p-6 w-full max-w-md z-10 space-y-4 animate-scale-up">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-teal-400" />
              <span>Complete Study Session</span>
            </h3>
            <p className="text-xs text-gray-400">
              You are completing: <span className="font-semibold text-white">{completingSession.topic}</span>
            </p>
            <div>
              <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Study Notes (Optional)
              </label>
              <textarea
                placeholder="Key takeaways, formulas reviewed, topics to revise..."
                value={completionNotes}
                onChange={(e) => setCompletionNotes(e.target.value)}
                className="input-field h-24 resize-none"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button onClick={() => setCompletingSession(null)} className="btn-secondary py-1.5 text-xs">
                Cancel
              </button>
              <button onClick={handleCompleteSession} className="btn-primary py-1.5 text-xs bg-teal-500 hover:bg-teal-400">
                Log Session
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
