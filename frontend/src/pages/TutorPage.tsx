import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  Plus,
  HelpCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

export const TutorPage: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [activeSession, setActiveSession] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [sessRes, subjRes] = await Promise.all([
        api.tutor.listSessions(),
        api.subjects.list(),
      ]);
      setSessions(sessRes);
      setSubjects(subjRes);
      if (sessRes.length > 0) {
        handleSelectSession(sessRes[0].id);
      }
    } catch (err: any) {
      toast.error('Failed to load tutor data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSelectSession = async (id: string) => {
    try {
      const fullSess = await api.tutor.getSession(id);
      setActiveSession(fullSess);
      setMessages(fullSess.messages || []);
    } catch (err: any) {
      toast.error('Failed to fetch chat details: ' + err.message);
    }
  };

  const handleCreateSession = async () => {
    try {
      const sub = subjects.find((s) => s.id === selectedSubject);
      const title = sub ? `Tutor Session: ${sub.name}` : 'General Q&A Session';
      
      const newSess = await api.tutor.createSession({
        subject_id: selectedSubject || undefined,
        title,
      });

      setSessions([newSess, ...sessions]);
      setActiveSession(newSess);
      setMessages([]);
      toast.success('New tutor session started!');
    } catch (err: any) {
      toast.error('Could not start session: ' + err.message);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending || !activeSession) return;

    const userMsgText = input;
    setInput('');
    setSending(true);

    // Optimistic user message render
    const tempUserMsg = {
      id: String(Date.now()),
      role: 'user',
      content: userMsgText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const replyMsg = await api.tutor.sendMessage(activeSession.id, userMsgText);
      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, replyMsg]);
      
      // Update session title locally if needed
      if (messages.length === 0) {
        const firstLine = userMsgText.slice(0, 30) + (userMsgText.length > 30 ? '...' : '');
        setSessions(sessions.map((s) => (s.id === activeSession.id ? { ...s, title: firstLine } : s)));
      }
    } catch (err: any) {
      toast.error('Tutor failed to respond: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  // Helper to format chat message text (supports basic headers, bullet lists)
  const renderMessageContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Check headers
      if (line.startsWith('## ')) {
        return <h3 key={idx} className="text-sm font-bold text-teal-300 mt-3 mb-1">{line.slice(3)}</h3>;
      }
      if (line.startsWith('# ')) {
        return <h2 key={idx} className="text-base font-extrabold text-purple-300 mt-4 mb-2">{line.slice(2)}</h2>;
      }
      // Check bullet items
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li key={idx} className="text-xs text-gray-300 ml-4 list-disc my-0.5">
            {line.slice(2)}
          </li>
        );
      }
      if (/^\d+\.\s/.test(line)) {
        return (
          <li key={idx} className="text-xs text-gray-300 ml-4 list-decimal my-0.5">
            {line.replace(/^\d+\.\s/, '')}
          </li>
        );
      }
      // Regular paragraph
      return line.trim() === '' ? <div key={idx} className="h-2" /> : <p key={idx} className="text-xs text-gray-200 leading-relaxed my-1">{line}</p>;
    });
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-purple-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-[calc(100vh-140px)] animate-fade-in">
      {/* Session sidebar */}
      <div className="md:col-span-1 glass-card p-4 flex flex-col justify-between h-full overflow-hidden">
        <div className="space-y-4 flex-1 flex flex-col min-h-0">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 shrink-0">
            <MessageSquare className="h-4.5 w-4.5 text-purple-400" />
            <span>Tutor Sessions</span>
          </h3>

          <div className="space-y-2 shrink-0">
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="input-field py-2 text-xs bg-dark-800"
            >
              <option value="">General (No subject)</option>
              {subjects.map((sub) => (
                <option key={sub.id} value={sub.id}>
                  {sub.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleCreateSession}
              className="w-full btn-primary py-2 text-xs flex items-center justify-center gap-1.5"
            >
              <Plus className="h-4 w-4" />
              <span>Start Session</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
            {sessions.length === 0 ? (
              <p className="text-xs text-gray-500 text-center py-8">No chat history. Start a new session!</p>
            ) : (
              sessions.map((sess) => (
                <button
                  key={sess.id}
                  onClick={() => handleSelectSession(sess.id)}
                  className={`w-full text-left p-3 rounded-xl border text-xs truncate transition-all ${
                    activeSession?.id === sess.id
                      ? 'bg-purple-500/10 text-purple-300 border-purple-500/30'
                      : 'bg-glass-white border-glass-border text-gray-400 hover:bg-glass-hover hover:text-white'
                  }`}
                >
                  {sess.title}
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="md:col-span-3 glass-card flex flex-col justify-between h-full overflow-hidden">
        {!activeSession ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <HelpCircle className="h-12 w-12 text-gray-600 mb-3 animate-float" />
            <h4 className="font-bold text-white text-base">Concept Clarifications?</h4>
            <p className="text-xs text-gray-500 max-w-xs mt-1">
              Select or start a tutor session on the left. Type complex formulas or definitions, and the AI agent explains with analogies.
            </p>
          </div>
        ) : (
          <>
            {/* Session Header */}
            <div className="px-6 py-4 border-b border-glass-border bg-dark-900/10 flex items-center justify-between shrink-0">
              <div className="min-w-0">
                <h4 className="font-bold text-sm text-white truncate">{activeSession.title}</h4>
                <span className="text-[10px] text-teal-400 font-mono">Agent Status: Ready</span>
              </div>
            </div>

            {/* Bubble Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12 text-gray-500 space-y-2">
                  <Sparkles className="h-8 w-8 mx-auto text-purple-500/60 animate-pulse" />
                  <p className="text-xs">Start the chat! Ask the AI Tutor anything about your study subjects.</p>
                </div>
              )}
              {messages.map((msg) => {
                const isUser = msg.role === 'user';
                return (
                  <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 border text-xs shadow-md ${
                        isUser
                          ? 'bg-purple-600/20 border-purple-500/30 text-white rounded-br-none'
                          : 'bg-glass-white border-glass-border text-gray-200 rounded-bl-none'
                      }`}
                    >
                      {!isUser && (
                        <div className="flex items-center gap-1.5 text-[9px] text-purple-400 font-mono mb-1">
                          <Sparkles className="h-3 w-3" />
                          <span>AI TUTOR</span>
                        </div>
                      )}
                      <div className="space-y-1">{renderMessageContent(msg.content)}</div>
                    </div>
                  </div>
                );
              })}
              {sending && (
                <div className="flex justify-start">
                  <div className="bg-glass-white border border-glass-border rounded-2xl rounded-bl-none px-4 py-3 max-w-[80%] text-xs shadow-md">
                    <span className="text-purple-400 animate-pulse font-mono">Tutor is thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message input panel */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-glass-border bg-dark-950/20 flex gap-2 shrink-0">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask your concept questions here..."
                className="input-field py-2.5 text-xs flex-1"
                disabled={sending}
              />
              <button
                type="submit"
                disabled={sending || !input.trim()}
                className="btn-primary px-4 py-2 flex items-center justify-center shrink-0"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
};
