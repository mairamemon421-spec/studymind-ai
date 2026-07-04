import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { Terminal, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import toast from 'react-hot-toast';

export const AgentLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async (pageNum = 1) => {
    try {
      setLoading(true);
      const res = await api.logs.list(pageNum, 15);
      setLogs(res.logs);
      setTotal(res.total);
      setPage(res.page);
    } catch (err: any) {
      toast.error('Failed to load agent logs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const totalPages = Math.ceil(total / 15) || 1;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between border-b border-glass-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Terminal className="h-6 w-6 text-purple-400" />
            <span>Multi-Agent Activity Feed</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Real-time execution log of study coordinator, planners, chat tutors, and analysts.
          </p>
        </div>

        <button
          onClick={() => fetchLogs(page)}
          className="p-2 rounded-xl bg-glass-white hover:bg-glass-hover text-gray-400 hover:text-white transition-colors"
          title="Refresh Feed"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {/* Terminal View Container */}
      <div className="glass-card bg-[#050511]/90 border border-purple-500/20 shadow-purple-glow/5 rounded-2xl overflow-hidden font-mono text-xs flex flex-col h-[520px]">
        {/* Terminal Header */}
        <div className="bg-dark-950 px-4 py-3 border-b border-glass-border flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-red-500/80" />
            <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
            <div className="h-3 w-3 rounded-full bg-green-500/80" />
            <span className="text-gray-500 text-[10px] ml-2">studymind-coordinator-shell.log</span>
          </div>
          <span className="text-[10px] text-teal-400">ACTIVE SESSION</span>
        </div>

        {/* Terminal logs list */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {loading ? (
            <div className="flex h-full items-center justify-center">
              <span className="text-purple-400 animate-pulse">CONNECTING TO AGENT ORCHESTRATOR...</span>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-20 text-gray-600">
              <p>&gt; No agent activity logs recorded yet.</p>
              <p className="text-[10px] mt-1">&gt; Generate a study plan or start a chat session to trigger agent pipelines.</p>
            </div>
          ) : (
            logs.map((log) => {
              const dateStr = new Date(log.created_at).toLocaleTimeString();
              const isSuccess = log.status === 'success';
              return (
                <div key={log.id} className="space-y-1 hover:bg-white/[0.02] p-1.5 rounded transition-colors border-l-2 border-transparent hover:border-purple-500/30">
                  <div className="flex items-start justify-between flex-wrap gap-2 text-gray-400">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">[{dateStr}]</span>
                      <span className="text-purple-400 font-bold">@{log.agent_name}</span>
                      <span className="text-teal-500">&gt; {log.action}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {log.duration_ms > 0 && (
                        <span className="text-[10px] text-gray-600 font-sans">{log.duration_ms}ms</span>
                      )}
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                        isSuccess 
                          ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' 
                          : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                      }`}>
                        {log.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="pl-6 space-y-1">
                    {log.input_summary && (
                      <div className="text-gray-500">
                        <span className="text-purple-600/70">IN:</span> {log.input_summary}
                      </div>
                    )}
                    {log.output_summary && (
                      <div className="text-gray-300">
                        <span className="text-teal-600/70">OUT:</span> {log.output_summary}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
          <div ref={terminalEndRef} />
        </div>
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-3 shrink-0">
          <button
            disabled={page === 1}
            onClick={() => fetchLogs(page - 1)}
            className="p-2 rounded-xl bg-glass-white border border-glass-border hover:bg-glass-hover disabled:opacity-50 transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-xs font-mono text-gray-400">
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page === totalPages}
            onClick={() => fetchLogs(page + 1)}
            className="p-2 rounded-xl bg-glass-white border border-glass-border hover:bg-glass-hover disabled:opacity-50 transition-colors"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
};
