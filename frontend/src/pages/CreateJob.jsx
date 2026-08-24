import React, { useState } from 'react';
import { Briefcase, CheckCircle2, ArrowRight, AlertCircle, Plus } from 'lucide-react';
import { api } from '../services/api';

export default function CreateJob({ onNavigate, setSelectedJobId }) {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [createdJob, setCreatedJob] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setError("Please provide a job description.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await api.createJob({ 
        title: title.trim() || undefined, 
        company: company.trim() || undefined, 
        description: description.trim() 
      });
      setCreatedJob(res.data);
      if (setSelectedJobId) setSelectedJobId(res.data.id);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save job description.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Create Job Position
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Add a job description. Requirements, mandatory skills, and experience criteria will be automatically structured.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!createdJob ? (
        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Job Title
              </label>
              <input
                type="text"
                placeholder="e.g. Senior Java Backend Developer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Company Name
              </label>
              <input
                type="text"
                placeholder="e.g. FinTech Global"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">
              Job Description Text
            </label>
            <textarea
              rows={10}
              placeholder="Paste raw Job Description text here including required skills, qualifications, experience, and responsibilities..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-mono leading-relaxed resize-none shadow-sm"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => onNavigate('studio')}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-1.5 px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-xs font-medium transition shadow-sm cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{loading ? "Processing..." : "Save Job Description"}</span>
            </button>
          </div>
        </form>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
          <div className="flex items-center space-x-2 text-emerald-600">
            <CheckCircle2 className="w-5 h-5" />
            <h2 className="text-base font-bold text-slate-900">
              Job Description Saved Successfully
            </h2>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3 text-xs">
            <div className="font-bold text-slate-900 text-sm">
              {createdJob.title} ({createdJob.company || 'Company'})
            </div>

            <div>
              <span className="font-semibold text-slate-700 block mb-1">Required Skills:</span>
              <div className="flex flex-wrap gap-1.5">
                {(createdJob.structured_requirements?.required_skills || []).map((s, idx) => (
                  <span key={idx} className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded text-[11px]">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <span className="font-semibold text-slate-700 block mb-1">Minimum Experience:</span>
              <span className="text-slate-600">{createdJob.structured_requirements?.experience?.minimum_years || 0} years</span>
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setCreatedJob(null);
                setTitle('');
                setCompany('');
                setDescription('');
              }}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition cursor-pointer"
            >
              Add Another Job
            </button>
            <button
              onClick={() => onNavigate('studio')}
              className="flex items-center space-x-1.5 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition cursor-pointer"
            >
              <span>Go to Screening Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
