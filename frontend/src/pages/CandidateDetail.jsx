import React, { useState, useEffect } from 'react';
import { ArrowLeft, CheckCircle2, XCircle, AlertTriangle, ShieldCheck, FileText, Check, Award, Briefcase, GraduationCap } from 'lucide-react';
import { api } from '../services/api';

export default function CandidateDetail({ onNavigate, matchId }) {
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (matchId) {
      loadDetail();
    } else {
      setLoading(false);
    }
  }, [matchId]);

  const loadDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getMatchDetail(matchId);
      setMatch(res.data);
    } catch (err) {
      console.error("Failed to load match detail:", err);
      setError("Evaluation record could not be loaded.");
    } finally {
      setLoading(false);
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

  if (loading) {
    return (
      <div className="text-center py-20 text-slate-500 text-sm">
        Loading candidate evaluation report...
      </div>
    );
  }

  if (error || !match) {
    return (
      <div className="max-w-xl mx-auto text-center py-16 bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-4">
        <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto" />
        <h3 className="text-base font-bold text-slate-900">Evaluation Report Not Found</h3>
        <p className="text-xs text-slate-500">
          Please run the screening process or select a candidate from the rankings table to view detailed evidence.
        </p>
        <button
          onClick={() => onNavigate('ranking')}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium transition"
        >
          Go to Candidate Rankings
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back Button */}
      <button
        onClick={() => onNavigate('ranking')}
        className="flex items-center space-x-1.5 text-xs text-slate-500 hover:text-slate-900 transition font-medium"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Candidate Rankings</span>
      </button>

      {/* Hero Header Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {match.candidate_name}
              </h1>
              <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${getBadgeColor(match.recommendation)}`}>
                {match.recommendation.replace('_', ' ')}
              </span>
            </div>
            <p className="text-slate-500 text-xs mt-1">
              Position: <span className="text-slate-800 font-semibold">{match.job_title}</span>
            </p>
          </div>

          <div className="flex items-center space-x-4 bg-slate-50 border border-slate-200 px-5 py-3 rounded-xl">
            <div>
              <span className="block text-[11px] text-slate-500 font-medium">Match Score</span>
              <span className="text-2xl font-extrabold text-blue-600">
                {match.overall_score.toFixed(0)}%
              </span>
            </div>
            <div className="h-8 w-px bg-slate-200" />
            <div>
              <span className="block text-[11px] text-slate-500 font-medium">Confidence</span>
              <span className="text-sm font-bold text-emerald-600">
                {(match.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        {match.critical_requirement_missing && (
          <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-xs flex items-start space-x-2.5">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600" />
            <div>
              <span className="font-semibold">Mandatory Requirement Gap:</span> Candidate lacks one or more required skills. Score and ranking reflect this critical qualification gap.
            </div>
          </div>
        )}

        {/* Executive Summary */}
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs text-slate-700 leading-relaxed">
          <span className="font-bold text-slate-900 mr-1.5">Evaluation Summary:</span>
          {match.explanation}
        </div>
      </div>

      {/* Multi-Component Score Breakdown */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900">
          Transparent Multi-Category Score Breakdown
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          <ScoreBar label="Required Skills (40% Weight)" score={match.scores.required_skills} />
          <ScoreBar label="Experience Duration (25% Weight)" score={match.scores.experience} />
          <ScoreBar label="Education Background (10% Weight)" score={match.scores.education} />
          <ScoreBar label="Responsibilities Alignment (10% Weight)" score={match.scores.responsibilities} />
          <ScoreBar label="Semantic & Domain Fit (10% Weight)" score={match.scores.semantic_match} />
          <ScoreBar label="Preferred Skills Bonus (5% Weight)" score={match.scores.preferred_skills} />
        </div>
      </div>

      {/* Matched vs Missing Evidence */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Matched Requirements with Evidence Quotes */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-emerald-700">
            <CheckCircle2 className="w-4 h-4" />
            <h3 className="text-sm font-bold">
              Matched Requirements ({match.matched_requirements.length})
            </h3>
          </div>

          <div className="space-y-3">
            {match.matched_requirements.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No exact requirement matches identified.</p>
            ) : (
              match.matched_requirements.map((req, idx) => (
                <div key={idx} className="bg-emerald-50/50 border border-emerald-100 p-3 rounded-lg space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-900">{req.requirement}</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                      {req.importance}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 bg-white p-2 rounded border border-emerald-100 italic">
                    "{req.evidence}"
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Missing Requirements & Gaps */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-rose-700">
            <XCircle className="w-4 h-4" />
            <h3 className="text-sm font-bold">
              Missing Requirements & Gaps ({match.missing_requirements.length})
            </h3>
          </div>

          <div className="space-y-3">
            {match.missing_requirements.length === 0 ? (
              <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-lg text-center space-y-1">
                <Check className="w-5 h-5 text-emerald-600 mx-auto" />
                <p className="text-xs font-semibold text-emerald-800">Complete Qualification Match</p>
                <p className="text-[11px] text-emerald-600">Candidate satisfies all listed job criteria.</p>
              </div>
            ) : (
              match.missing_requirements.map((req, idx) => (
                <div key={idx} className="bg-rose-50/50 border border-rose-100 p-3 rounded-lg space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-900">{req.requirement}</span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      req.importance === 'REQUIRED' 
                        ? 'bg-rose-100 text-rose-800' 
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {req.importance}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">
                    {req.evidence}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

function ScoreBar({ label, score }) {
  return (
    <div className="space-y-1 bg-slate-50 p-3 rounded-lg border border-slate-200">
      <div className="flex justify-between text-xs font-medium">
        <span className="text-slate-700">{label}</span>
        <span className="text-blue-700 font-bold">{score}%</span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
        <div
          className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  );
}
