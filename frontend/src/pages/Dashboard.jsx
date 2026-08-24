import React, { useState, useEffect } from 'react';
import { Briefcase, Users, CheckCircle2, Plus, Upload, ArrowRight, Trash2 } from 'lucide-react';
import { api } from '../services/api';

export default function Dashboard({ onNavigate, setSelectedJobId }) {
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [jobsRes, resumesRes] = await Promise.all([
        api.listJobs(),
        api.listResumes()
      ]);
      setJobs(jobsRes.data);
      setResumes(resumesRes.data);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteJob = async (jobId, e) => {
    e.stopPropagation();
    try {
      await api.deleteJob(jobId);
      loadData();
    } catch (err) {
      console.error("Failed to delete job:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Job Positions
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage open positions and view structured candidate screening pipelines.
          </p>
        </div>
        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => onNavigate('upload')}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-medium transition shadow-sm cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Resumes</span>
          </button>
          <button
            onClick={() => onNavigate('create-job')}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition shadow-sm cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Post New Job</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
          <span className="text-xs font-medium text-slate-500">Active Positions</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{jobs.length}</p>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
          <span className="text-xs font-medium text-slate-500">Candidate Profiles</span>
          <p className="text-2xl font-bold text-slate-900 mt-1">{resumes.length}</p>
        </div>

        <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
          <span className="text-xs font-medium text-slate-500">Screening Pipeline</span>
          <p className="text-2xl font-bold text-emerald-600 mt-1">Ready</p>
        </div>
      </div>

      {/* Jobs Grid */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 mb-4">
          Positions List
        </h2>

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs">Loading positions...</div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-xl">
            <Briefcase className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-slate-700">No job positions created yet</h3>
            <p className="text-xs text-slate-500 mt-0.5 mb-3">Add a job description to start evaluating candidates.</p>
            <button
              onClick={() => onNavigate('create-job')}
              className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition cursor-pointer"
            >
              Post First Job
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job) => (
              <div 
                key={job.id} 
                className="bg-slate-50 border border-slate-200 p-4 rounded-xl space-y-3 hover:border-slate-300 transition"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">{job.title}</h3>
                    <span className="text-xs text-slate-500">{job.company || 'Company'}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteJob(job.id, e)}
                    className="text-slate-400 hover:text-rose-600 transition cursor-pointer"
                    title="Delete Job"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex flex-wrap gap-1">
                  {(job.structured_requirements?.required_skills || []).slice(0, 4).map((skill, idx) => (
                    <span key={idx} className="text-[11px] bg-white text-slate-700 border border-slate-200 px-2 py-0.5 rounded">
                      {skill}
                    </span>
                  ))}
                  {(job.structured_requirements?.required_skills || []).length > 4 && (
                    <span className="text-[10px] text-slate-400 self-center">
                      +{(job.structured_requirements?.required_skills || []).length - 4} more
                    </span>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-200 flex justify-between items-center text-xs">
                  <span className="text-slate-500 text-[11px]">
                    Min Exp: {job.structured_requirements?.experience?.minimum_years || 0} yrs
                  </span>
                  <button
                    onClick={() => {
                      setSelectedJobId(job.id);
                      onNavigate('ranking');
                    }}
                    className="text-blue-600 hover:underline font-medium flex items-center space-x-1 cursor-pointer"
                  >
                    <span>View Candidates</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
