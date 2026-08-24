import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, Trash2, Users } from 'lucide-react';
import { api } from '../services/api';

export default function UploadResumes({ onNavigate, selectedJobId }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [resumesList, setResumesList] = useState([]);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const res = await api.listResumes();
      setResumesList(res.data);
    } catch (err) {
      console.error("Failed to list resumes:", err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    try {
      setUploading(true);
      setError(null);
      setSuccessMsg(null);

      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const res = await api.uploadResumes(formData);
      setSuccessMsg(`Successfully uploaded & parsed ${res.data.length} candidate resume(s).`);
      setFiles([]);
      loadResumes();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload or parsing failed for one or more files.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteResume(id);
      loadResumes();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Resume Library
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload and manage candidate resumes in PDF (.pdf) or Text (.txt) formats.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-700 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Upload Dropzone */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm text-center space-y-4">
        <div className="border-2 border-dashed border-slate-200 hover:border-blue-500 rounded-xl p-8 space-y-3 bg-slate-50 transition">
          <Upload className="w-8 h-8 text-slate-400 mx-auto" />
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Upload Candidate Resumes</h3>
            <p className="text-xs text-slate-500 mt-0.5">Drag and drop files here, or browse from your computer (.pdf, .txt)</p>
          </div>

          <input
            type="file"
            multiple
            accept=".pdf,.txt"
            onChange={handleFileChange}
            className="hidden"
            id="resume-lib-upload"
          />

          <label
            htmlFor="resume-lib-upload"
            className="inline-block px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-medium cursor-pointer shadow-sm transition"
          >
            Browse Files
          </label>
        </div>

        {files.length > 0 && (
          <div className="pt-2 max-w-md mx-auto space-y-2 text-left">
            <p className="text-xs text-slate-500 font-medium">Selected files ({files.length}):</p>
            {files.map((f, i) => (
              <div key={i} className="flex justify-between text-xs text-slate-700 bg-slate-50 px-3 py-1.5 rounded border border-slate-200">
                <span className="truncate">{f.name}</span>
                <span className="text-slate-400">{(f.size / 1024).toFixed(0)} KB</span>
              </div>
            ))}

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full mt-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-xs font-medium transition shadow-sm cursor-pointer"
            >
              {uploading ? "Parsing candidate resumes..." : "Upload & Parse Selected Files"}
            </button>
          </div>
        )}
      </div>

      {/* Uploaded Resumes Pool Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-sm font-bold text-slate-900">
            Candidate Profiles in Library ({resumesList.length})
          </h2>
          {resumesList.length > 0 && (
            <button
              onClick={() => onNavigate('studio')}
              className="text-xs text-blue-600 hover:underline font-medium flex items-center space-x-1 cursor-pointer"
            >
              <span>Go to Screening Studio</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>

        {resumesList.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">
            No resumes uploaded yet. Upload PDF or TXT files above to populate candidate profiles.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {resumesList.map((r) => (
              <div key={r.id} className="p-3.5 flex justify-between items-center hover:bg-slate-50 transition text-xs">
                <div className="flex items-center space-x-3">
                  <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900 text-xs">{r.candidate_name}</h4>
                    <p className="text-[11px] text-slate-500">{r.file_name} • {r.file_type}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-medium">
                    Parsed
                  </span>
                  <button
                    onClick={() => handleDelete(r.id)}
                    className="text-slate-400 hover:text-rose-600 transition cursor-pointer"
                    title="Delete Resume"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
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
