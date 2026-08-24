import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export const api = {
  // Health
  getHealth: () => axios.get(`${API_BASE}/health`),

  // Jobs
  listJobs: () => axios.get(`${API_BASE}/jobs`),
  getJob: (id) => axios.get(`${API_BASE}/jobs/${id}`),
  createJob: (jobData) => axios.post(`${API_BASE}/jobs`, jobData),
  deleteJob: (id) => axios.delete(`${API_BASE}/jobs/${id}`),

  // Resumes
  listResumes: () => axios.get(`${API_BASE}/resumes`),
  getResume: (id) => axios.get(`${API_BASE}/resumes/${id}`),
  uploadResumes: (formData) => axios.post(`${API_BASE}/resumes`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteResume: (id) => axios.delete(`${API_BASE}/resumes/${id}`),

  // Screening & Matches
  screenCandidates: (jobId, resumeIds = null) => 
    axios.post(`${API_BASE}/jobs/${jobId}/screen`, resumeIds ? { resume_ids: resumeIds } : {}),

  getRankedCandidates: (jobId, params = {}) => 
    axios.get(`${API_BASE}/jobs/${jobId}/candidates`, { params }),

  getMatchDetail: (matchId) => axios.get(`${API_BASE}/matches/${matchId}`)
};
