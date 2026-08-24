import React, { useState, useEffect } from 'react';
import { 
  Briefcase, Upload, FileText, CheckCircle2, AlertCircle, 
  ArrowRight, ShieldCheck, RefreshCw, Plus, ExternalLink, Trash2
} from 'lucide-react';
import { api } from '../services/api';

export default function ScreeningStudio({ onNavigate, setSelectedJobId, setSelectedMatchId }) {
  const [jobs, setJobs] = useState([]);
  const [selectedJobIdLocal, setSelectedJobIdLocal] = useState('');
  
  // New Job Input
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  
  // Resumes Upload
  const [files, setFiles] = useState([]);
  const [existingResumes, setExistingResumes] = useState([]);
  const [selectedResumeIds, setSelectedResumeIds] = useState([]);
  
  // Execution & Results
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState(null);
  const [rankedCandidates, setRankedCandidates] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [jobsRes, resumesRes] = await Promise.all([
        api.listJobs(),
        api.listResumes()
      ]);
      setJobs(jobsRes.data);
      setExistingResumes(resumesRes.data);
      if (jobsRes.data.length > 0) {
        setSelectedJobIdLocal(jobsRes.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load initial data:", err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleToggleResumeSelect = (id) => {
    setSelectedResumeIds(prev => 
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const handleSelectAllResumes = () => {
    if (selectedResumeIds.length === existingResumes.length) {
      setSelectedResumeIds([]);
    } else {
      setSelectedResumeIds(existingResumes.map(r => r.id));
    }
  };

  const handleRunScreening = async () => {
    setError(null);
    setRankedCandidates(null);

    let activeJobId = selectedJobIdLocal;

    // Validate Job Description
    if (!activeJobId || jobDescription.trim()) {
      if (!jobDescription.trim()) {
        setError("Please select an existing job position or provide a job description.");
        return;
      }

      try {
        setLoading(true);
        setStatusMessage("Processing job description and requirements...");
        const jobRes = await api.createJob({
          title: jobTitle.trim() || undefined,
          company: company.trim() || undefined,
          description: jobDescription.trim()
        });
        activeJobId = jobRes.data.id;
        setSelectedJobIdLocal(activeJobId);
        if (setSelectedJobId) setSelectedJobId(activeJobId);
        const updatedJobs = await api.listJobs();
        setJobs(updatedJobs.data);
      } catch (err) {
        setLoading(false);
        setError(err.response?.data?.detail || "Failed to save job position.");
        return;
      }
    } else {
      if (setSelectedJobId) setSelectedJobId(activeJobId);
    }

    // Validate Resumes
    if (files.length === 0 && selectedResumeIds.length === 0 && existingResumes.length === 0) {
      setError("Please upload at least one candidate resume (.pdf or .txt) to evaluate.");
      return;
    }

    try {
      setLoading(true);
      let targetResumeIds = [...selectedResumeIds];

      // Upload any newly selected files
      if (files.length > 0) {
        setStatusMessage(`Uploading and parsing ${files.length} resume(s)...`);
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        const uploadRes = await api.uploadResumes(formData);
        const newIds = uploadRes.data.map(r => r.id);
        targetResumeIds = [...targetResumeIds, ...newIds];
        setFiles([]);
        const updatedRes = await api.listResumes();
        setExistingResumes(updatedRes.data);
      }

      // If no specific subset selected, screen all target/existing
      const finalResumeIds = targetResumeIds.length > 0 ? targetResumeIds : null;

      // Run screening engine strictly for these resumes
      setStatusMessage("Evaluating candidates against role requirements...");
      await api.screenCandidates(activeJobId, finalResumeIds);

      // Fetch ranked candidates
      setStatusMessage("Generating match justifications...");
      const rankedRes = await api.getRankedCandidates(activeJobId);
      setRankedCandidates(rankedRes.data);

    } catch (err) {
      console.error("Screening error:", err);
      setError(err.response?.data?.detail || "Screening process failed.");
    } finally {
      setLoading(false);
      setStatusMessage('');
    }
  };

  const getRecommendationBadge = (rec) => {
    switch (rec) {
      case 'STRONG_MATCH':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'MATCH':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'PARTIAL_MATCH':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-rose-50 text-rose-700 border-rose-200';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Screening Studio
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Provide a job description, upload candidate resumes, and evaluate candidates with transparent matching scores.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-xs hover:underline cursor-pointer">Dismiss</button>
        </div>
      )}

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Card: Job Description */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-4 h-4 text-slate-700" />
                <h2 className="font-semibold text-slate-900 text-sm">Job Description</h2>
              </div>
            </div>

            {jobs.length > 0 && (
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1.5">
                  Select Existing Position
                </label>
                <select
                  value={selectedJobIdLocal}
                  onChange={(e) => setSelectedJobIdLocal(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-500 shadow-sm"
                >
                  <option value="">-- Or enter a new job description below --</option>
                  {jobs.map(j => (
                    <option key={j.id} value={j.id}>{j.title} ({j.company || 'Company'})</option>
                  ))}
                </select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Job Title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => {
                    setJobTitle(e.target.value);
                    if (selectedJobIdLocal) setSelectedJobIdLocal('');
                  }}
                  placeholder="e.g. Senior Java Developer"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Company
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => {
                    setCompany(e.target.value);
                    if (selectedJobIdLocal) setSelectedJobIdLocal('');
                  }}
                  placeholder="e.g. FinTech Corp"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                Job Requirements & Responsibilities
              </label>
              <textarea
                rows={9}
                value={jobDescription}
                onChange={(e) => {
                  setJobDescription(e.target.value);
                  if (selectedJobIdLocal) setSelectedJobIdLocal('');
                }}
                placeholder="Paste the job description text here (required technical skills, minimum experience, education, responsibilities)..."
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-mono leading-relaxed resize-none shadow-sm"
              />
            </div>
          </div>
        </div>

        {/* Right Card: Candidate Resumes */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Upload className="w-4 h-4 text-slate-700" />
                <h2 className="font-semibold text-slate-900 text-sm">Candidate Resumes</h2>
              </div>
              <span className="text-xs text-slate-500">
                {existingResumes.length} in library
              </span>
            </div>

            {/* Dropzone */}
            <div className="border-2 border-dashed border-slate-200 hover:border-blue-500 rounded-xl p-6 text-center space-y-2.5 bg-slate-50 transition">
              <FileText className="w-8 h-8 text-slate-400 mx-auto" />
              <div>
                <p className="text-xs font-semibold text-slate-700">
                  Select candidate resumes
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Accepts .pdf and .txt files
                </p>
              </div>

              <input
                type="file"
                multiple
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="studio-file-input"
              />
              <label
                htmlFor="studio-file-input"
                className="inline-block px-4 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-lg cursor-pointer shadow-sm transition"
              >
                Browse Files
              </label>
            </div>

            {/* Selected New Files */}
            {files.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-xs font-medium text-blue-600">
                  Selected for upload ({files.length}):
                </span>
                <div className="space-y-1 max-h-32 overflow-y-auto pr-1">
                  {files.map((file, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-slate-50 border border-slate-200 px-3 py-1 rounded text-xs text-slate-700">
                      <span className="truncate">{file.name}</span>
                      <span className="text-[10px] text-slate-400">{(file.size / 1024).toFixed(0)} KB</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Existing Resumes in Library */}
            {existingResumes.length > 0 && files.length === 0 && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs text-slate-500 font-medium">
                  <span>Candidate Pool ({existingResumes.length})</span>
                  <button 
                    type="button"
                    onClick={handleSelectAllResumes} 
                    className="hover:underline text-blue-600 cursor-pointer"
                  >
                    {selectedResumeIds.length === existingResumes.length ? "Deselect all" : "Select all"}
                  </button>
                </div>
                <div className="space-y-1 max-h-36 overflow-y-auto pr-1">
                  {existingResumes.map((r) => {
                    const isChecked = selectedResumeIds.includes(r.id);
                    return (
                      <label 
                        key={r.id} 
                        className={`flex justify-between items-center px-3 py-1.5 rounded text-xs border cursor-pointer transition ${
                          isChecked 
                            ? 'bg-blue-50 border-blue-200 text-blue-900 font-medium' 
                            : 'bg-slate-50 border-slate-200 text-slate-700'
                        }`}
                      >
                        <div className="flex items-center space-x-2 truncate">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => handleToggleResumeSelect(r.id)}
                            className="rounded border-slate-300 text-blue-600 focus:ring-0"
                          />
                          <span className="truncate">{r.candidate_name}</span>
                        </div>
                        <span className="text-[10px] text-slate-400">{r.file_type}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}

            {existingResumes.length === 0 && files.length === 0 && (
              <div className="text-center py-4 text-xs text-slate-400">
                No resumes in pool. Browse and upload resumes above.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Screen Action Button */}
      <div className="flex flex-col items-center justify-center pt-2">
        <button
          onClick={handleRunScreening}
          disabled={loading}
          className="inline-flex items-center space-x-2 px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-md transition cursor-pointer"
        >
          {loading ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <CheckCircle2 className="w-3.5 h-3.5" />
          )}
          <span>{loading ? (statusMessage || 'Screening in progress...') : 'Screen Candidates'}</span>
        </button>
        {statusMessage && (
          <p className="text-xs text-slate-500 mt-2 font-medium">
            {statusMessage}
          </p>
        )}
      </div>

      {/* Results Leaderboard */}
      {rankedCandidates && (
        <div className="space-y-6 pt-6 border-t border-slate-200">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <div>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                Screened Candidates ({rankedCandidates.length})
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Evaluated and ranked strictly from the uploaded candidate resumes.
              </p>
            </div>
            <button
              onClick={() => onNavigate('ranking')}
              className="text-xs font-medium text-blue-600 hover:underline flex items-center space-x-1 cursor-pointer"
            >
              <span>Open full rankings table</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-4">
            {rankedCandidates.map((candidate) => (
              <div 
                key={candidate.candidate_id}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3.5 transition hover:border-slate-300"
              >
                {/* Top Bar */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                  <div className="flex items-center space-x-3.5">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-sm">
                      #{candidate.rank}
                    </div>

                    <div>
                      <div className="flex items-center space-x-2.5">
                        <h3 className="font-bold text-slate-900 text-base">
                          {candidate.candidate_name}
                        </h3>
                        <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-semibold ${getRecommendationBadge(candidate.recommendation)}`}>
                          {candidate.recommendation.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {candidate.experience_years} years experience • {candidate.matched_skills_count}/{candidate.total_required_skills} mandatory skills matched
                      </p>
                    </div>
                  </div>

                  <div className="text-right self-end sm:self-auto">
                    <span className="text-xl font-bold text-slate-900">
                      {candidate.overall_score.toFixed(0)}%
                    </span>
                    <span className="text-[11px] text-slate-400 block -mt-1">Match Score</span>
                  </div>
                </div>

                {/* Recruiter Justification */}
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-700 leading-relaxed">
                  <span className="font-semibold text-slate-900 mr-1.5">Evaluation:</span>
                  {candidate.explanation || `${candidate.candidate_name} matches ${candidate.overall_score}% of requirements.`}
                </div>

                {/* Footer Bar */}
                <div className="flex justify-between items-center text-xs pt-1">
                  <div className="text-slate-500">
                    {candidate.critical_requirement_missing ? (
                      <span className="text-amber-600 font-medium flex items-center space-x-1">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>Missing mandatory requirement</span>
                      </span>
                    ) : (
                      <span className="text-emerald-600 font-medium flex items-center space-x-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Core requirements met</span>
                      </span>
                    )}
                  </div>

                  <button
                    onClick={() => {
                      if (setSelectedMatchId) setSelectedMatchId(candidate.match_id);
                      if (onNavigate) onNavigate('detail');
                    }}
                    className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1 cursor-pointer"
                  >
                    <span>View evidence details</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
