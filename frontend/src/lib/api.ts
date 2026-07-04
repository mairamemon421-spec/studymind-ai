// Frontend API client connected exclusively to Supabase & FastAPI AI services
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Helper to get auth headers containing Supabase JWT session token
async function getHeaders() {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    ...await getHeaders(),
    ...options.headers,
  };
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'API request failed' }));
    throw new Error(errorData.detail || 'API request failed');
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  // Auth
  auth: {
    register: async (data: any) => {
      // 1. Sign up via Supabase Auth
      const { data: authData, error } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
        options: {
          data: {
            full_name: data.full_name,
            study_hours_per_day: data.study_hours_per_day || 4,
          }
        }
      });
      if (error) throw new Error(error.message);
      if (!authData.user) throw new Error('Registration failed');

      // The postgres trigger handles public.users table insert automatically.
      // Fetch profile to verify
      const { data: profile } = await supabase
        .from('users')
        .select('*')
        .eq('id', authData.user.id)
        .single();

      return {
        access_token: authData.session?.access_token || '',
        user: profile || {
          id: authData.user.id,
          email: data.email,
          full_name: data.full_name,
          study_hours_per_day: data.study_hours_per_day || 4,
        },
      };
    },
    login: async (data: any) => {
      const { data: authData, error } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      });
      if (error) throw new Error(error.message);
      if (!authData.user) throw new Error('Login failed');

      // Fetch profile
      const { data: profile } = await supabase
        .from('users')
        .select('*')
        .eq('id', authData.user.id)
        .single();

      return {
        access_token: authData.session?.access_token || '',
        user: profile || {
          id: authData.user.id,
          email: data.email,
          full_name: authData.user.user_metadata?.full_name || '',
          study_hours_per_day: 4,
        },
      };
    },
    me: async () => {
      const { data: { user }, error } = await supabase.auth.getUser();
      if (error || !user) throw new Error('Not authenticated');

      const { data: profile } = await supabase
        .from('users')
        .select('*')
        .eq('id', user.id)
        .single();

      return profile || {
        id: user.id,
        email: user.email || '',
        full_name: user.user_metadata?.full_name || '',
        study_hours_per_day: 4,
      };
    },
  },

  // Subjects
  subjects: {
    list: async () => {
      const { data, error } = await supabase
        .from('subjects')
        .select('*')
        .order('created_at', { ascending: false });
      if (error) throw new Error(error.message);
      return data || [];
    },
    create: async (data: any) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      const newSubject = {
        user_id: user.id,
        name: data.name,
        description: data.description || '',
        color: data.color || '#9047ff',
        icon: data.icon || 'BookOpen',
        difficulty: data.difficulty || 3,
        mastery_score: 0.0,
      };

      const { data: inserted, error } = await supabase
        .from('subjects')
        .insert([newSubject])
        .select()
        .single();

      if (error) throw new Error(error.message);
      return inserted;
    },
    update: async (id: string, data: any) => {
      const { data: updated, error } = await supabase
        .from('subjects')
        .update(data)
        .eq('id', id)
        .select()
        .single();
      if (error) throw new Error(error.message);
      return updated;
    },
    delete: async (id: string) => {
      const { error } = await supabase.from('subjects').delete().eq('id', id);
      if (error) throw new Error(error.message);
    },
  },

  // Exams
  exams: {
    list: async () => {
      const { data, error } = await supabase
        .from('exams')
        .select('*')
        .order('exam_date', { ascending: true });
      if (error) throw new Error(error.message);
      return data || [];
    },
    create: async (data: any) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      const newExam = {
        user_id: user.id,
        subject_id: data.subject_id,
        title: data.title,
        exam_date: data.exam_date,
        importance: data.importance || 3,
        notes: data.notes || '',
      };

      const { data: inserted, error } = await supabase
        .from('exams')
        .insert([newExam])
        .select()
        .single();

      if (error) throw new Error(error.message);
      return inserted;
    },
    update: async (id: string, data: any) => {
      const { data: updated, error } = await supabase
        .from('exams')
        .update(data)
        .eq('id', id)
        .select()
        .single();
      if (error) throw new Error(error.message);
      return updated;
    },
    delete: async (id: string) => {
      const { error } = await supabase.from('exams').delete().eq('id', id);
      if (error) throw new Error(error.message);
    },
  },

  // Study plans
  plans: {
    list: async () => {
      const { data: plans, error } = await supabase
        .from('study_plans')
        .select('*')
        .order('created_at', { ascending: false });
      if (error) throw new Error(error.message);

      const planList = [];
      for (const plan of (plans || [])) {
        const { data: sessions } = await supabase
          .from('plan_sessions')
          .select('*')
          .eq('plan_id', plan.id);
        planList.push({
          ...plan,
          sessions: sessions || [],
        });
      }
      return planList;
    },
    get: async (id: string) => {
      const { data: plan, error } = await supabase
        .from('study_plans')
        .select('*')
        .eq('id', id)
        .single();
      if (error) throw new Error(error.message);

      const { data: sessions } = await supabase
        .from('plan_sessions')
        .select('*')
        .eq('plan_id', id)
        .order('session_date', { ascending: true })
        .order('start_time', { ascending: true });

      return {
        ...plan,
        sessions: sessions || [],
      };
    },
    generate: async (data: any) => {
      // Planning AI Coordinator runs on backend and inserts study_plans and plan_sessions directly to Supabase.
      return request<any>('/plans/generate', { method: 'POST', body: JSON.stringify(data) });
    },
    completeSession: async (_planId: string, sessionId: string, notes?: string) => {
      const updatePayload = {
        completed: true,
        completed_at: new Date().toISOString(),
        notes: notes || '',
      };
      const { error } = await supabase
        .from('plan_sessions')
        .update(updatePayload)
        .eq('id', sessionId);
      if (error) throw new Error(error.message);
      return { status: 'completed', session_id: sessionId };
    },
  },

  // Tutor
  tutor: {
    createSession: async (data: any) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      const newSession = {
        user_id: user.id,
        subject_id: data.subject_id || null,
        title: data.title || 'New Chat',
      };

      const { data: inserted, error } = await supabase
        .from('chat_sessions')
        .insert([newSession])
        .select()
        .single();

      if (error) throw new Error(error.message);
      return inserted;
    },
    listSessions: async () => {
      const { data, error } = await supabase
        .from('chat_sessions')
        .select('*')
        .order('updated_at', { ascending: false });
      if (error) throw new Error(error.message);
      return data || [];
    },
    getSession: async (id: string) => {
      const { data: session, error } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('id', id)
        .single();
      if (error) throw new Error(error.message);

      const { data: messages } = await supabase
        .from('chat_messages')
        .select('*')
        .eq('session_id', id)
        .order('created_at', { ascending: true });

      return {
        ...session,
        messages: messages || [],
      };
    },
    sendMessage: async (sessionId: string, content: string) => {
      // AI Tutor Agent response generation and chat history saving is executed by the FastAPI backend
      return request<any>(`/tutor/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      });
    },
  },

  // Quizzes
  quizzes: {
    list: async () => {
      const { data, error } = await supabase
        .from('quizzes')
        .select('*')
        .order('created_at', { ascending: false });
      if (error) throw new Error(error.message);
      return data || [];
    },
    get: async (id: string) => {
      const { data: quiz, error } = await supabase
        .from('quizzes')
        .select('*')
        .eq('id', id)
        .single();
      if (error) throw new Error(error.message);

      const { data: questions } = await supabase
        .from('quiz_questions')
        .select('*')
        .eq('quiz_id', id)
        .order('order_index', { ascending: true });

      const parsedQuestions = (questions || []).map(q => ({
        ...q,
        options: typeof q.options === 'string' ? JSON.parse(q.options) : q.options,
      }));

      return {
        ...quiz,
        questions: parsedQuestions,
      };
    },
    generate: async (data: any) => {
      // Quiz agent runs on backend and inserts the generated quiz/questions directly to Supabase
      return request<any>('/quiz/generate', { method: 'POST', body: JSON.stringify(data) });
    },
    submit: async (id: string, answers: any[]) => {
      // Quiz grading and analytical feedback is processed on backend and updated directly in Supabase
      return request<any>(`/quiz/${id}/submit`, {
        method: 'POST',
        body: JSON.stringify({ answers }),
      });
    },
  },

  // Progress & Analytics
  progress: {
    get: async () => {
      // Dashboard progress stats are queried and calculated on the FastAPI backend
      return request<any>('/progress');
    },
  },

  // Logs
  logs: {
    list: async (page = 1, pageSize = 20) => {
      const from = (page - 1) * pageSize;
      const to = from + pageSize - 1;

      const { data: logs, count, error } = await supabase
        .from('agent_logs')
        .select('*', { count: 'exact' })
        .order('created_at', { ascending: false })
        .range(from, to);

      if (error) throw new Error(error.message);

      return {
        logs: logs || [],
        total: count || 0,
        page,
        page_size: pageSize,
      };
    },
  },

  // PDF download helper link URL containing auth token query param
  pdfUrl: (planId: string) => {
    // Session token is required to authenticate the file stream request
    return `${BASE_URL}/export/pdf/${planId}`;
  },
};
