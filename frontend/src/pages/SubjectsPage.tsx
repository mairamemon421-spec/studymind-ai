import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { BookOpen, Calendar, Trash2, Plus, AlertCircle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

export const SubjectsPage: React.FC = () => {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [exams, setExams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Subject form
  const [subName, setSubName] = useState('');
  const [subDesc, setSubDesc] = useState('');
  const [subColor, setSubColor] = useState('#9047ff');
  const [subDifficulty, setSubDifficulty] = useState(3);

  // Exam form
  const [examTitle, setExamTitle] = useState('');
  const [examSubjectId, setExamSubjectId] = useState('');
  const [examDate, setExamDate] = useState('');
  const [examImportance, setExamImportance] = useState(3);
  const [examNotes, setExamNotes] = useState('');

  const [activeTab, setActiveTab] = useState<'subjects' | 'exams'>('subjects');

  const colorPalette = [
    '#9047ff', // Purple
    '#14b8a6', // Teal
    '#3b82f6', // Blue
    '#f59e0b', // Amber
    '#ef4444', // Red
    '#ec4899', // Pink
  ];

  const fetchData = async () => {
    try {
      setLoading(true);
      const [subRes, examRes] = await Promise.all([
        api.subjects.list(),
        api.exams.list(),
      ]);
      setSubjects(subRes);
      setExams(examRes);
      if (subRes.length > 0 && !examSubjectId) {
        setExamSubjectId(subRes[0].id);
      }
    } catch (err: any) {
      toast.error('Failed to load data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subName.trim()) {
      toast.error('Subject name is required');
      return;
    }
    try {
      const newSub = await api.subjects.create({
        name: subName,
        description: subDesc || undefined,
        color: subColor,
        difficulty: subDifficulty,
      });
      setSubjects([newSub, ...subjects]);
      if (!examSubjectId) setExamSubjectId(newSub.id);
      setSubName('');
      setSubDesc('');
      toast.success('Subject created successfully!');
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  const handleDeleteSubject = async (id: string) => {
    if (!confirm('Are you sure you want to delete this subject? All related exams will be removed.')) return;
    try {
      await api.subjects.delete(id);
      setSubjects(subjects.filter((s) => s.id !== id));
      setExams(exams.filter((e) => e.subject_id !== id));
      toast.success('Subject deleted');
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  const handleAddExam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!examTitle.trim() || !examSubjectId || !examDate) {
      toast.error('Title, Subject, and Date are required');
      return;
    }
    try {
      const newExam = await api.exams.create({
        title: examTitle,
        subject_id: examSubjectId,
        exam_date: examDate,
        importance: examImportance,
        notes: examNotes || undefined,
      });
      setExams([newExam, ...exams]);
      setExamTitle('');
      setExamDate('');
      setExamNotes('');
      toast.success('Exam scheduled successfully!');
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  const handleDeleteExam = async (id: string) => {
    if (!confirm('Cancel this exam schedule?')) return;
    try {
      await api.exams.delete(id);
      setExams(exams.filter((e) => e.id !== id));
      toast.success('Exam schedule removed');
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-purple-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Tabs */}
      <div className="flex items-center justify-between border-b border-glass-border pb-4">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('subjects')}
            className={`text-lg font-bold pb-2 border-b-2 transition-all ${
              activeTab === 'subjects'
                ? 'text-white border-purple-500'
                : 'text-gray-500 border-transparent hover:text-gray-300'
            }`}
          >
            Subjects ({subjects.length})
          </button>
          <button
            onClick={() => setActiveTab('exams')}
            className={`text-lg font-bold pb-2 border-b-2 transition-all ${
              activeTab === 'exams'
                ? 'text-white border-purple-500'
                : 'text-gray-500 border-transparent hover:text-gray-300'
            }`}
          >
            Exams ({exams.length})
          </button>
        </div>
        <button
          onClick={fetchData}
          className="p-2 rounded-xl bg-glass-white hover:bg-glass-hover text-gray-400 hover:text-white transition-colors"
          title="Refresh"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {activeTab === 'subjects' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Create form */}
          <div className="glass-card p-6 h-fit lg:col-span-1">
            <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
              <Plus className="h-5 w-5 text-purple-400" />
              <span>Add New Subject</span>
            </h3>
            <form onSubmit={handleAddSubject} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Subject Name</label>
                <input
                  type="text"
                  placeholder="e.g. Linear Algebra"
                  value={subName}
                  onChange={(e) => setSubName(e.target.value)}
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Description</label>
                <textarea
                  placeholder="Topics, syllabus, notes..."
                  value={subDesc}
                  onChange={(e) => setSubDesc(e.target.value)}
                  className="input-field h-20 resize-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Difficulty Level (1-5)</label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((lvl) => (
                    <button
                      key={lvl}
                      type="button"
                      onClick={() => setSubDifficulty(lvl)}
                      className={`flex-1 py-1.5 rounded-lg text-xs font-mono font-bold transition-all border ${
                        subDifficulty === lvl
                          ? 'bg-purple-500/20 text-purple-300 border-purple-500'
                          : 'bg-dark-800 border-glass-border text-gray-400 hover:bg-glass-white'
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-2">Accent Color</label>
                <div className="flex gap-2">
                  {colorPalette.map((col) => (
                    <button
                      key={col}
                      type="button"
                      onClick={() => setSubColor(col)}
                      className={`h-6 w-6 rounded-full border-2 transition-all ${
                        subColor === col ? 'border-white scale-110 shadow-lg' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: col }}
                    />
                  ))}
                </div>
              </div>

              <button type="submit" className="w-full btn-primary mt-2">
                Create Subject
              </button>
            </form>
          </div>

          {/* Subjects list */}
          <div className="lg:col-span-2 space-y-4">
            {subjects.length === 0 ? (
              <div className="glass-card p-12 text-center text-gray-500">
                <BookOpen className="h-10 w-10 mx-auto text-gray-600 mb-3" />
                <p className="text-sm">No subjects yet. Create your first subject above!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {subjects.map((sub) => (
                  <div key={sub.id} className="glass-card p-5 flex flex-col justify-between h-44 relative overflow-hidden group">
                    {/* Background accent tab */}
                    <div 
                      className="absolute left-0 top-0 bottom-0 w-1.5"
                      style={{ backgroundColor: sub.color }}
                    />
                    
                    <div>
                      <div className="flex justify-between items-start pl-2">
                        <h4 className="font-bold text-white text-base truncate pr-6">{sub.name}</h4>
                        <button
                          onClick={() => handleDeleteSubject(sub.id)}
                          className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all shrink-0"
                          title="Delete Subject"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <p className="text-xs text-gray-400 pl-2 mt-1 line-clamp-2">{sub.description || 'No description provided'}</p>
                    </div>

                    <div className="pl-2 mt-4 flex items-center justify-between border-t border-glass-border/60 pt-3 shrink-0">
                      <span className="text-[10px] font-mono bg-purple-500/10 text-purple-300 px-2 py-0.5 rounded-full">
                        Difficulty: {sub.difficulty}/5
                      </span>
                      <span className="text-[10px] font-mono bg-teal-500/10 text-teal-400 px-2 py-0.5 rounded-full">
                        Mastery: {Math.round(sub.mastery_score * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Create form */}
          <div className="glass-card p-6 h-fit lg:col-span-1">
            <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
              <Calendar className="h-5 w-5 text-purple-400" />
              <span>Schedule Exam</span>
            </h3>
            {subjects.length === 0 ? (
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-start gap-2 text-xs">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <span>You must create at least one subject before scheduling exams.</span>
              </div>
            ) : (
              <form onSubmit={handleAddExam} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-1">Exam Title</label>
                  <input
                    type="text"
                    placeholder="e.g. Midterm 1"
                    value={examTitle}
                    onChange={(e) => setExamTitle(e.target.value)}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-1">Subject</label>
                  <select
                    value={examSubjectId}
                    onChange={(e) => setExamSubjectId(e.target.value)}
                    className="input-field bg-dark-800"
                  >
                    {subjects.map((sub) => (
                      <option key={sub.id} value={sub.id}>
                        {sub.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-1">Exam Date</label>
                  <input
                    type="date"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-1">Importance (1-5)</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((lvl) => (
                      <button
                        key={lvl}
                        type="button"
                        onClick={() => setExamImportance(lvl)}
                        className={`flex-1 py-1.5 rounded-lg text-xs font-mono font-bold transition-all border ${
                          examImportance === lvl
                            ? 'bg-purple-500/20 text-purple-300 border-purple-500'
                            : 'bg-dark-800 border-glass-border text-gray-400 hover:bg-glass-white'
                        }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-1">Notes</label>
                  <textarea
                    placeholder="Chapters, topics covered, location..."
                    value={examNotes}
                    onChange={(e) => setExamNotes(e.target.value)}
                    className="input-field h-20 resize-none"
                  />
                </div>

                <button type="submit" className="w-full btn-primary mt-2">
                  Schedule Exam
                </button>
              </form>
            )}
          </div>

          {/* Exams list */}
          <div className="lg:col-span-2 space-y-4">
            {exams.length === 0 ? (
              <div className="glass-card p-12 text-center text-gray-500">
                <Calendar className="h-10 w-10 mx-auto text-gray-600 mb-3" />
                <p className="text-sm">No exams scheduled yet. Add exams to sync with study planners!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {exams.map((exam) => {
                  const matchingSub = subjects.find((s) => s.id === exam.subject_id);
                  const isSoon = Math.ceil((new Date(exam.exam_date).getTime() - new Date().getTime()) / (1000 * 3600 * 24)) <= 5;
                  return (
                    <div key={exam.id} className="glass-card p-5 flex flex-col md:flex-row justify-between md:items-center gap-4 relative overflow-hidden group">
                      {matchingSub && (
                        <div 
                          className="absolute left-0 top-0 bottom-0 w-1.5"
                          style={{ backgroundColor: matchingSub.color }}
                        />
                      )}
                      
                      <div className="pl-2 space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-white text-base">{exam.title}</h4>
                          <span className="text-[10px] text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-full font-semibold">
                            {matchingSub?.name || 'Unknown Subject'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">{exam.notes || 'No special notes'}</p>
                      </div>

                      <div className="flex items-center gap-4 pl-2 md:pl-0 shrink-0">
                        <div className="text-left md:text-right">
                          <span className="text-xs text-gray-500 block">Exam Date</span>
                          <span className={`text-xs font-mono font-semibold ${isSoon ? 'text-red-400' : 'text-gray-300'}`}>
                            {new Date(exam.exam_date).toLocaleDateString(undefined, {
                              weekday: 'short',
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                        </div>

                        <button
                          onClick={() => handleDeleteExam(exam.id)}
                          className="p-2 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all shrink-0"
                          title="Remove Exam"
                        >
                          <Trash2 className="h-4.5 w-4.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
