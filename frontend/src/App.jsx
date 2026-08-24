import React, { useState } from 'react';
import { 
  Briefcase, Upload, ListOrdered, SlidersHorizontal, Layers
} from 'lucide-react';

import ScreeningStudio from './pages/ScreeningStudio';
import Dashboard from './pages/Dashboard';
import CreateJob from './pages/CreateJob';
import UploadResumes from './pages/UploadResumes';
import CandidateRanking from './pages/CandidateRanking';
import CandidateDetail from './pages/CandidateDetail';

export default function App() {
  const [activeTab, setActiveTab] = useState('studio');
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedMatchId, setSelectedMatchId] = useState(null);

  const handleNavigate = (tab) => {
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Brand Title */}
          <div 
            onClick={() => handleNavigate('studio')}
            className="flex items-center space-x-3 cursor-pointer select-none group"
          >
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white shadow-sm group-hover:bg-blue-700 transition">
              <Layers className="w-4 h-4" />
            </div>
            <span className="font-bold text-base tracking-tight text-slate-900">
              Smart Resume Screener
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <NavItem 
              icon={<SlidersHorizontal className="w-4 h-4" />} 
              label="Screening Studio" 
              active={activeTab === 'studio'} 
              onClick={() => handleNavigate('studio')} 
            />
            <NavItem 
              icon={<ListOrdered className="w-4 h-4" />} 
              label="Candidate Rankings" 
              active={activeTab === 'ranking'} 
              onClick={() => handleNavigate('ranking')} 
            />
            <NavItem 
              icon={<Briefcase className="w-4 h-4" />} 
              label="Job Positions" 
              active={activeTab === 'jobs'} 
              onClick={() => handleNavigate('jobs')} 
            />
            <NavItem 
              icon={<Upload className="w-4 h-4" />} 
              label="Resume Library" 
              active={activeTab === 'resumes'} 
              onClick={() => handleNavigate('resumes')} 
            />
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'studio' && (
          <ScreeningStudio 
            onNavigate={handleNavigate} 
            setSelectedJobId={setSelectedJobId} 
            setSelectedMatchId={setSelectedMatchId} 
          />
        )}
        {activeTab === 'ranking' && (
          <CandidateRanking 
            onNavigate={handleNavigate} 
            selectedJobId={selectedJobId} 
            setSelectedMatchId={setSelectedMatchId} 
          />
        )}
        {activeTab === 'jobs' && (
          <Dashboard 
            onNavigate={handleNavigate} 
            setSelectedJobId={setSelectedJobId} 
          />
        )}
        {activeTab === 'create-job' && (
          <CreateJob 
            onNavigate={handleNavigate} 
            setSelectedJobId={setSelectedJobId} 
          />
        )}
        {activeTab === 'resumes' && (
          <UploadResumes 
            onNavigate={handleNavigate} 
            selectedJobId={selectedJobId} 
          />
        )}
        {activeTab === 'detail' && (
          <CandidateDetail 
            onNavigate={handleNavigate} 
            matchId={selectedMatchId} 
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 bg-white">
        Smart Resume Screener • Automated Parsing & Deterministic Evidence Engine
      </footer>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition cursor-pointer ${
        active 
          ? 'bg-slate-100 text-blue-700 font-semibold border border-slate-200' 
          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}
