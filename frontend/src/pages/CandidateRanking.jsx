import React, { useState, useEffect } from 'react';
import { Filter, RefreshCw, AlertTriangle, CheckCircle2, ExternalLink, Briefcase, Search } from 'lucide-react';
import { api } from '../services/api';

export default function CandidateRanking({ onNavigate, selectedJobId, setSelectedMatchId }) {
  const [candidates, setCandidates] = useState([]);
  const [job, setJob] = useState(null);
  const [allJobs, setAllJobs] = useState([]);
  const [activeJobId, setActiveJobId] = useState(selectedJobId || '');
  const [loading, setLoading] = useState(false);
  const [screening, setScreening] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [minScore, setMinScore] = useState('');
  const [recommendationFilter, setRecommendationFilter] = useState('');
  const [requireMandatory, setRequireMandatory] = useState(false);

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    if (activeJobId) {
      loadData(activeJobId);
    }
  }, [activeJobId, minScore, recommendationFilter, requireMandatory]);

  const loadJobs = async () => {
    try {
      const res = await api.listJobs();
      setAllJobs(res.data);
      if (!activeJobId && res.data.length > 0) {
        setActiveJobId(res.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load jobs:", err);
    }
  };

  const loadData = async (jobId) => {
    try {
      setLoading(true);
      const [jobRes, candRes] = await Promise.all([
        api.getJob(jobId),
        api.getRankedCandidates(jobId, {
          min_score: minScore ? parseFloat(minScore) : undefined,
          recommendation: recommendationFilter || undefined,
          require_all_mandatory: requireMandatory
        })
      ]);
      setJob(jobRes.data);
      setCandidates(candRes.data);
    } catch (err) {
      console.error("Failed to load rankings:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunScreening = async () => {
    if (!activeJobId) return;
    try {
      setScreening(true);
      await api.screenCandidates(activeJobId);
      loadData(activeJobId);
    } catch (err) {
      console.error("Screening failed:", err);
    } finally {
      setScreening(false);
    }
  };

  const getBadgeColor = (rec) => {
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

  const filteredCandidates = candidates.filter(c => {
    if (!searchTerm) return true;
    return c.candidate_name.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* Header & Job Selector */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Candidate Rankings
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Shortlist of evaluated candidates ranked by skill alignment, verified experience, and criteria compliance.
          </p>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          {allJobs.length > 0 && (
            <select
              value={activeJobId}
              onChange={(e) => setActiveJobId(e.target.value)}
              className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-medium text-slate-900 focus:outline-none focus:border-blue-500 shadow-sm"
            >
              {allJobs.map(j => (
                <option key={j.id} value={j.id}>{j.title} ({j.company || 'Company'})</option>
              ))}
            </select>
          )}

          <button
            onClick={handleRunScreening}
            disabled={screening || !activeJobId}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-xs font-medium transition shadow-sm cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${screening ? 'animate-spin' : ''}`} />
            <span>{screening ? 'Evaluating...' : 'Re-Screen Pool'}</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search candidate name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 w-48"
            />
          </div>

          <select
            value={recommendationFilter}
            onChange={(e) => setRecommendationFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Match Tiers</option>
            <option value="STRONG_MATCH">Strong Match</option>
            <option value="MATCH">Good Match</option>
            <option value="PARTIAL_MATCH">Partial Match</option>
            <option value="WEAK_MATCH">Weak Match</option>
          </select>

          <input
            type="number"
            placeholder="Min Score % (e.g. 70)"
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            className="w-32 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>

        <label className="flex items-center space-x-2 cursor-pointer text-slate-600 font-medium">
          <input
            type="checkbox"
            checked={requireMandatory}
            onChange={(e) => setRequireMandatory(e.target.checked)}
            className="rounded border-slate-300 text-blue-600 focus:ring-0"
          />
          <span>Exclude candidates with missing mandatory skills</span>
        </label>
      </div>

      {/* Candidate Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="text-center py-16 text-slate-400 text-sm">
            Loading candidate ranking...
          </div>
        ) : !activeJobId ? (
          <div className="text-center py-16 text-slate-400 text-sm space-y-3">
            <p>No job positions found. Create or select a job description to screen candidates.</p>
            <button
              onClick={() => onNavigate('create-job')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-medium"
            >
              Post Job Position
            </button>
          </div>
        ) : filteredCandidates.length === 0 ? (
          <div className="text-center py-16 text-slate-400 text-sm space-y-3">
            <p>No candidate match records found for this position.</p>
            <button
              onClick={handleRunScreening}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-medium"
            >
              Run Screening Now
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
                  <th className="py-3 px-4 w-12">Rank</th>
                  <th className="py-3 px-4">Candidate</th>
                  <th className="py-3 px-4">Match Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Core Skills</th>
                  <th className="py-3 px-4">Experience</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredCandidates.map((c) => (
                  <tr key={c.candidate_id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3.5 px-4 font-bold text-slate-600">
                      #{c.rank}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900 text-sm">
                        {c.candidate_name}
                      </div>
                      {c.critical_requirement_missing && (
                        <span className="inline-flex items-center space-x-1 text-[11px] text-amber-600 mt-0.5 font-medium">
                          <AlertTriangle className="w-3 h-3" />
                          <span>Missing mandatory requirement</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-slate-900 text-sm">
                        {c.overall_score.toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full border font-semibold text-[11px] ${getBadgeColor(c.recommendation)}`}>
                        {c.recommendation.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      <span className="font-medium text-emerald-600">{c.matched_skills_count}</span>
                      <span className="text-slate-400"> / {c.total_required_skills} matched</span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      {c.experience_years} yrs
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => {
                          setSelectedMatchId(c.match_id);
                          onNavigate('detail');
                        }}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition cursor-pointer"
                      >
                        <span>View Evidence</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
