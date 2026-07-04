import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { api } from '../lib/api';
import toast from 'react-hot-toast';
import { Lock, Mail, User, Sparkles, Clock } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [studyHours, setStudyHours] = useState(4);
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      if (isRegister) {
        const res = await api.auth.register({
          email,
          password,
          full_name: fullName || undefined,
          study_hours_per_day: studyHours,
        });
        login(res.access_token, res.user);
        toast.success('Registration successful! Welcome to StudyMind AI.');
      } else {
        const res = await api.auth.login({ email, password });
        login(res.access_token, res.user);
        toast.success('Logged in successfully!');
      }
      navigate('/');
    } catch (err: any) {
      toast.error(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 bg-gradient-mesh p-4 font-sans relative overflow-hidden">
      {/* Mesh gradients */}
      <div className="absolute top-[-30%] left-[-20%] h-[80vh] w-[80vw] rounded-full bg-purple-900/15 blur-[150px]" />
      <div className="absolute bottom-[-30%] right-[-20%] h-[80vh] w-[80vw] rounded-full bg-teal-900/15 blur-[150px]" />

      <div className="w-full max-w-md z-10">
        {/* Logo/Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex h-16 w-16 rounded-2xl bg-gradient-to-tr from-purple-600 to-teal-500 items-center justify-center font-bold text-white text-2xl shadow-purple-glow mb-4 animate-float">
            SM
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            {isRegister ? 'Create Your Account' : 'Welcome Back'}
          </h2>
          <p className="text-gray-400 mt-2 text-sm">
            {isRegister 
              ? 'Join StudyMind AI and customize your study plans.'
              : 'Log in to access your personalized study timetable & tutor.'}
          </p>
        </div>

        {/* Card wrapper */}
        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {isRegister && (
              <>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-purple-300 mb-2">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                    <input
                      type="text"
                      placeholder="Jane Doe"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="input-field pl-10"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-purple-300 mb-2">
                    Daily Study Target (Hours)
                  </label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                    <input
                      type="number"
                      min="1"
                      max="12"
                      value={studyHours}
                      onChange={(e) => setStudyHours(parseInt(e.target.value) || 4)}
                      className="input-field pl-10"
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-purple-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                <input
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-purple-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3 flex items-center justify-center gap-2 mt-4"
            >
              {loading ? (
                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  <span>{isRegister ? 'Register' : 'Log In'}</span>
                </>
              )}
            </button>
          </form>

          {/* Toggle login/register */}
          <div className="text-center mt-6">
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="text-xs text-purple-400 hover:text-purple-300 hover:underline transition-colors"
            >
              {isRegister 
                ? 'Already have an account? Sign In'
                : "Don't have an account? Sign Up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
