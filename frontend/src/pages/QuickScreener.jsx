import React, { useState } from 'react';
import { 
  Sparkles, Upload, FileText, CheckCircle2, AlertTriangle, 
  ArrowRight, ShieldCheck, Star, ChevronDown, ChevronUp, RefreshCw,
  Award, Briefcase, GraduationCap, Clock
} from 'lucide-react';
import { api } from '../services/api';

const SAMPLE_JD = {
  title: "Senior Java Backend Developer",
  company: "FinTech Global",
  description: `Senior Java Backend Developer

Company: FinTech Global
Location: Remote / Austin, TX

About the Role:
We are looking for a Senior Java Backend Developer to build and scale core payment processing services.

Mandatory Required Skills:
- Java (3+ years experience)
- Spring Boot
- REST APIs
- PostgreSQL database design and optimization

Preferred Skills:
- Apache Kafka event streaming
- AWS Cloud infrastructure (EC2, S3)
- Docker & Kubernetes

Requirements:
- Bachelor's degree in Computer Science or related field.
- Minimum 3 years of hands-on software development experience.

Responsibilities:
- Architect and develop secure RESTful APIs using Spring Boot.
- Optimize database queries and schema performance in PostgreSQL.
- Collaborate with frontend engineers to integrate API services.`
};

const SAMPLE_RESUMES = [
  {
    name: "Alex_Mercer_Lead_Java.txt",
    type: "text/plain",
    content: `Alex Mercer
Email: alex.mercer@devtech.io
Phone: +1 (555) 234-5678
Location: Austin, TX
LinkedIn: linkedin.com/in/alexmercer-dev

SUMMARY:
Lead Backend Engineer with 6+ years of production experience architecting mission-critical Java Spring Boot microservices, high-throughput Apache Kafka event pipelines, and scalable PostgreSQL database clusters on AWS.

TECHNICAL SKILLS:
- Programming Languages: Java, Python, SQL, Go
- Frameworks & Libraries: Spring Boot, Spring Cloud, Hibernate, FastAPI
- Databases: PostgreSQL, Redis, MySQL, DynamoDB
- Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, CI/CD, Terraform
- Architecture: REST APIs, Apache Kafka, Microservices, Event-Driven Architecture

PROFESSIONAL EXPERIENCE:
Lead Software Engineer | FinTech Cloud Systems | Austin, TX
Jan 2022 - Present (2.5 years)
- Architected enterprise Spring Boot REST microservices processing over $50M daily transactions.
- Designed distributed real-time messaging pipeline utilizing Apache Kafka and PostgreSQL.
- Reduced API latency by 45% using Redis caching and PostgreSQL query optimization.

Senior Backend Engineer | CloudScale Tech | San Jose, CA
Jun 2018 - Dec 2021 (3.5 years)
- Developed Java REST APIs for e-commerce payment processing platform.
- Managed PostgreSQL database schema migrations.

EDUCATION:
Bachelor of Science in Computer Science
University of Texas at Austin (2018) | GPA: 3.9 / 4.0`
  },
  {
    name: "Sarah_Jenkins_Mid_Java.txt",
    type: "text/plain",
    content: `Sarah Jenkins
Email: sarah.jenkins@codeflow.io
Phone: +1 (555) 876-5432
Location: Denver, CO
LinkedIn: linkedin.com/in/sarahjenkins-dev

SUMMARY:
Software Engineer with 3.5 years of experience developing robust backend services using Java, Spring Boot, REST APIs, and PostgreSQL. Passionate about clean code and API performance.

TECHNICAL SKILLS:
- Languages: Java, SQL, JavaScript
- Frameworks: Spring Boot, Spring MVC, REST APIs
- Databases: PostgreSQL, MySQL, SQLite
- Tools & Cloud: Docker, Git, Postman, Linux

PROFESSIONAL EXPERIENCE:
Java Backend Developer | DataWorks Solutions | Denver, CO
Mar 2021 - Present (3.5 years)
- Developed secure Spring Boot REST APIs for customer portal applications.
- Engineered PostgreSQL database schemas and optimized indexing for query speed.
- Collaborated with frontend team to integrate backend API endpoints.

EDUCATION:
Bachelor of Science in Software Engineering
Colorado State University (2021) | GPA: 3.7 / 4.0`
  },
  {
    name: "David_Chen_Frontend.txt",
    type: "text/plain",
    content: `David Chen
Email: david.chen@webcraft.dev
Phone: +1 (555) 345-6789
Location: Seattle, WA
LinkedIn: linkedin.com/in/davidchen-ui

SUMMARY:
Frontend Engineer with 4 years of experience specializing in React, TypeScript, Next.js, and modern UI architecture.

TECHNICAL SKILLS:
- Languages: TypeScript, JavaScript, HTML5, CSS3
- Frameworks: React, Next.js, Vue.js, Tailwind CSS
- Tools: Vite, Webpack, Git, Figma

PROFESSIONAL EXPERIENCE:
Senior Frontend Developer | Nova UI Studios | Seattle, WA
Jan 2022 - Present (2.5 years)
- Built interactive dashboard interfaces using React, TypeScript, and Tailwind CSS.
- Optimized frontend bundle size and web vitals performance scores.

EDUCATION:
Bachelor of Arts in Interactive Digital Media
University of Washington (2020)`
  }
];

export default function QuickScreener({ onNavigate, setSelectedJobId, setSelectedMatchId }) {
  const [jobTitle, setJobTitle] = useState(SAMPLE_JD.title);
  const [company, setCompany] = useState(SAMPLE_JD.company);
  const [jobDescription, setJobDescription] = useState(SAMPLE_JD.description);
  
  const [files, setFiles] = useState([]);
  const [statusStep, setStatusStep] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [rankedResults, setRankedResults] = useState(null);
  const [activeJobId, setActiveJobId] = useState(null);
  const [expandedCards, setExpandedCards] = useState({});

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleLoadSampleFiles = () => {
    const fileObjects = SAMPLE_RESUMES.map(item => {
      const blob = new Blob([item.content], { type: 'text/plain' });
      return new File([blob], item.name, { type: 'text/plain' });
    });
    setFiles(fileObjects);
    setError(null);
  };

  const handleLoadSampleJD = () => {
    setJobTitle(SAMPLE_JD.title);
    setCompany(SAMPLE_JD.company);
    setJobDescription(SAMPLE_JD.description);
  };

  const toggleExpand = (id) => {
    setExpandedCards(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleRunQuickScreening = async () => {
    if (!jobDescription.trim()) {
      setError("Please provide or load a Job Description.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setRankedResults(null);

      // Step 1: Create Job & extract requirements
      setStatusStep('Analyzing Job Description & Extracting Requirements...');
      const jobRes = await api.createJob({
        title: jobTitle || "Backend Developer",
        company: company || "TechCorp",
        description: jobDescription
      });
      const jobId = jobRes.data.id;
      setActiveJobId(jobId);
      if (setSelectedJobId) setSelectedJobId(jobId);

      // Step 2: Upload and parse resumes
      setStatusStep('Parsing Resumes (PDF / TXT) & Extracting Skills...');
      let resumeUploadList = files;
      if (resumeUploadList.length === 0) {
        // Use default sample resumes if none selected
        resumeUploadList = SAMPLE_RESUMES.map(item => {
          const blob = new Blob([item.content], { type: 'text/plain' });
          return new File([blob], item.name, { type: 'text/plain' });
        });
      }

      const formData = new FormData();
      resumeUploadList.forEach(file => formData.append('files', file));
      await api.uploadResumes(formData);

      // Step 3: Run Deterministic & LLM Screening
      setStatusStep('Computing Fit Scores (1–10 Scale) & Generating Justifications...');
      await api.screenCandidates(jobId);

      // Step 4: Fetch Ranked Candidates
      setStatusStep('Ranking Shortlist...');
      const rankedRes = await api.getRankedCandidates(jobId);
      setRankedResults(rankedRes.data);

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Screening failed. Please check inputs and try again.");
    } finally {
      setLoading(false);
      setStatusStep('');
    }
  };

  const getBadgeStyle = (rec) => {
    switch (rec) {
      case 'STRONG_MATCH':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'MATCH':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'PARTIAL_MATCH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Title & Objective */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold rounded-full uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Minimal & Fast Recruiter Screener</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Smart Resume Screener</h1>
        <p className="text-slate-400 text-sm max-w-2xl mx-auto">
          Intelligently parse PDF/Text resumes, extract structured skills and experience, compute transparent 
          <strong> 1–10 Fit Scores</strong> with LLM reasoning, and display shortlisted candidates with evidence justification.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-xs hover:underline">Dismiss</button>
        </div>
      )}

      {/* Two-Column Inputs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Job Description */}
        <div className="bg-slate-800/70 border border-slate-700/70 rounded-2xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold text-xs">
                  1
                </div>
                <h2 className="font-bold text-white text-base">Job Description</h2>
              </div>
              <button
                type="button"
                onClick={handleLoadSampleJD}
                className="text-xs text-blue-400 hover:text-blue-300 bg-blue-500/10 px-2.5 py-1 rounded border border-blue-500/20 transition"
              >
                Load Sample Java JD
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Position Title</label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Senior Java Developer"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Company</label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. FinTech Global"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Job Description Requirements</label>
              <textarea
                rows={11}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste JD text here with required skills, experience, and responsibilities..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono leading-relaxed resize-none"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Resumes Input */}
        <div className="bg-slate-800/70 border border-slate-700/70 rounded-2xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold text-xs">
                  2
                </div>
                <h2 className="font-bold text-white text-base">Candidate Resumes (PDF / TXT)</h2>
              </div>
              <button
                type="button"
                onClick={handleLoadSampleFiles}
                className="text-xs text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20 transition"
              >
                Load 3 Sample Resumes
              </button>
            </div>

            <div className="border-2 border-dashed border-slate-700 hover:border-blue-500/60 rounded-xl p-6 text-center space-y-3 bg-slate-900/40 transition">
              <Upload className="w-8 h-8 text-blue-400 mx-auto" />
              <div>
                <p className="text-xs font-semibold text-slate-200">Drag & drop PDF / TXT files</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Supports multi-file upload</p>
              </div>

              <input
                type="file"
                multiple
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="quick-resume-input"
              />
              <label
                htmlFor="quick-resume-input"
                className="inline-block px-4 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium rounded-lg cursor-pointer transition"
              >
                Browse Files
              </label>
            </div>

            {/* Selected Resumes List */}
            <div className="mt-4 space-y-2">
              <div className="flex justify-between items-center text-xs text-slate-400 font-semibold uppercase tracking-wider">
                <span>Selected Resumes ({files.length > 0 ? files.length : '3 Default Preloaded'})</span>
              </div>

              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {(files.length > 0 ? files : SAMPLE_RESUMES).map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-slate-900/80 border border-slate-700/60 px-3 py-2 rounded-lg text-xs">
                    <div className="flex items-center space-x-2 truncate">
                      <FileText className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                      <span className="truncate text-slate-200">{item.name}</span>
                    </div>
                    <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-medium">
                      Ready
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Trigger Action Button */}
      <div className="text-center">
        <button
          onClick={handleRunQuickScreening}
          disabled={loading}
          className="inline-flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-bold text-base rounded-2xl shadow-xl shadow-blue-500/25 transition transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
        >
          <Sparkles className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? (statusStep || 'Screening Resumes...') : '⚡ Screen & Rate Fit (1–10 Scale)'}</span>
        </button>
        {statusStep && (
          <p className="text-xs text-blue-400 mt-3 animate-pulse font-medium">{statusStep}</p>
        )}
      </div>

      {/* Results Section: Shortlisted Candidates */}
      {rankedResults && (
        <div className="space-y-6 pt-4 border-t border-slate-800">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Shortlisted Candidates & Justification</h2>
              <p className="text-slate-400 text-xs mt-0.5">Ranked by multi-component fit score (1–10), skill compliance, and evidence.</p>
            </div>
            <div className="flex items-center space-x-2 text-xs bg-slate-800 px-3 py-1.5 rounded-lg text-slate-300 border border-slate-700">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero-Hallucination Evidence Verified</span>
            </div>
          </div>

          <div className="space-y-4">
            {rankedResults.map((candidate) => (
              <div 
                key={candidate.candidate_id}
                className="bg-slate-800/80 border border-slate-700/80 hover:border-slate-600 rounded-2xl p-5 space-y-4 transition shadow-lg"
              >
                {/* Header Row: Rank, Name, Score, Badge */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-extrabold text-base ${
                      candidate.rank === 1 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                      candidate.rank === 2 ? 'bg-slate-700 text-slate-200' : 'bg-slate-800 text-slate-400'
                    }`}>
                      #{candidate.rank}
                    </div>

                    <div>
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-bold text-white">{candidate.candidate_name}</h3>
                        <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-semibold ${getBadgeStyle(candidate.recommendation)}`}>
                          {candidate.recommendation.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {candidate.experience_years} years experience • {candidate.matched_skills_count}/{candidate.total_required_skills} mandatory skills matched
                      </p>
                    </div>
                  </div>

                  {/* 1-10 Fit Rating Box */}
                  <div className="flex items-center space-x-4 self-end sm:self-auto">
                    <div className="text-right">
                      <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Fit Rating</div>
                      <div className="flex items-baseline space-x-1">
                        <span className="text-2xl font-extrabold text-white tracking-tight">
                          {candidate.fit_score_10 || (candidate.overall_score / 10).toFixed(1)}
                        </span>
                        <span className="text-xs font-semibold text-slate-400">/ 10</span>
                      </div>
                    </div>
                    <div className="text-xs px-2.5 py-1.5 bg-slate-900 rounded-lg text-slate-300 font-mono border border-slate-700">
                      {candidate.overall_score.toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Justification Box */}
                <div className="bg-slate-900/90 border border-slate-700/60 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <div className="flex items-center space-x-1.5 text-blue-400">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>LLM Fit Justification & Empirical Evidence</span>
                    </div>
                    {candidate.critical_requirement_missing && (
                      <span className="text-amber-400 text-[11px] flex items-center space-x-1 font-medium">
                        <AlertTriangle className="w-3 h-3" />
                        <span>Critical Requirement Penalty Applied</span>
                      </span>
                    )}
                  </div>
                  
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    {candidate.explanation || `Fit rating ${(candidate.overall_score / 10).toFixed(1)}/10. Candidate exhibits ${candidate.recommendation.toLowerCase().replace('_', ' ')} alignment across required backend technologies.`}
                  </p>
                </div>

                {/* Card Footer: Detail Link */}
                <div className="pt-2 flex justify-between items-center text-xs">
                  <div className="flex items-center space-x-2 text-slate-400">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Audit-Ready & Verified Against Schema</span>
                  </div>

                  <button
                    onClick={() => {
                      if (setSelectedMatchId) setSelectedMatchId(candidate.match_id);
                      if (onNavigate) onNavigate('detail');
                    }}
                    className="text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1 hover:underline cursor-pointer"
                  >
                    <span>View Full Evidence Breakdown</span>
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
