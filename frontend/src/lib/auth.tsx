import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from './api';

interface User {
  id: string;
  email: string;
  full_name?: string;
  study_hours_per_day: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch profile from public.users table in Supabase
  const fetchProfile = async (uuid: string, email: string, metadata: any) => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', uuid)
        .single();

      if (data) {
        return {
          id: data.id,
          email: data.email,
          full_name: data.full_name,
          study_hours_per_day: data.study_hours_per_day,
        };
      }
    } catch (e) {
      console.warn('Could not fetch user profile from public.users:', e);
    }
    return {
      id: uuid,
      email: email,
      full_name: metadata?.full_name || '',
      study_hours_per_day: metadata?.study_hours_per_day || 4,
    };
  };

  const login = (token: string, userData: User) => {
    // Compatibility helper for LoginPage
    setUser(userData);
  };

  const refreshUser = async () => {
    const { data: { user: authUser } } = await supabase.auth.getUser();
    if (authUser) {
      const profile = await fetchProfile(authUser.id, authUser.email || '', authUser.user_metadata);
      setUser(profile);
    } else {
      setUser(null);
    }
  };

  const logout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) console.error('Sign out error:', error);
    setUser(null);
  };

  useEffect(() => {
    // Check session on mount
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      if (session?.user) {
        const profile = await fetchProfile(session.user.id, session.user.email || '', session.user.user_metadata);
        setUser(profile);
      }
      setLoading(false);
    });

    // Listen for auth session changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        const profile = await fetchProfile(session.user.id, session.user.email || '', session.user.user_metadata);
        setUser(profile);
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
