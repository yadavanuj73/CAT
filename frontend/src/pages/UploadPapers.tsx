import React, { useState } from 'react';
import { usePapers, useUploadPaper, useExtractPaper } from '../hooks/usePapers';
import { Link } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  RefreshCw,
  ShieldCheck,
  History,
  Lock,
} from 'lucide-react';

export const UploadPapers: React.FC = () => {
  const { data: papersData, isLoading } = usePapers();
  const uploadMutation = useUploadPaper();
  const extractMutation = useExtractPaper();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [year, setYear] = useState<number>(2024);
  const [slot, setSlot] = useState<string>('Slot 1');
  const [sourceName, setSourceName] = useState<string>('IIM Official');
  const [sourceType] = useState<string>('official');
  const [allowSharing, setAllowSharing] = useState<boolean>(true);
  const [termsAccepted, setTermsAccepted] = useState<boolean>(true);
  const [msg, setMsg] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setMsg({ type: 'error', text: 'Only PDF documents are supported.' });
        return;
      }
      setSelectedFile(file);
      setMsg(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    if (!termsAccepted) {
      setMsg({ type: 'error', text: 'Please confirm document authenticity and eligibility.' });
      return;
    }

    setMsg(null);
    try {
      const res = await uploadMutation.mutateAsync({
        file: selectedFile,
        metadata: {
          title: `CAT ${year} ${slot}`,
          year,
          slot,
          source: sourceType,
          allow_sharing: allowSharing,
          terms_accepted: termsAccepted,
        },
      });

      if ((res as any).is_duplicate) {
        setMsg({
          type: 'info',
          text: `Exact duplicate detected: An identical paper already exists in the shared database. Reused existing verified questions.`,
        });
      } else {
        setMsg({
          type: 'info',
          text: `Paper uploaded successfully. Extracting questions, verifying mathematics, and promoting to Shared Bank...`,
        });
        if (res && (res as any).id) {
          await handleExtract((res as any).id);
        }
      }
      setSelectedFile(null);
    } catch {
      setMsg({ type: 'error', text: 'Failed to upload paper. Please check file format.' });
    }
  };

  const handleExtract = async (paperId: string) => {
    try {
      const res = await extractMutation.mutateAsync(paperId);
      const resData = res as any;
      if (resData?.status === 'duplicate_reused') {
        setMsg({
          type: 'info',
          text: `Exact duplicate paper detected. Reused ${resData.questions_count} verified questions from shared question bank.`,
        });
      } else {
        setMsg({
          type: 'success',
          text: `Extracted ${resData?.questions_count || ''} questions. Multi-stage verification completed and eligible questions promoted to shared bank.`,
        });
      }
    } catch {
      setMsg({ type: 'error', text: 'Extraction or verification failed.' });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">Upload Authentic Historical Papers</h1>
        <p className="text-sm text-gray-500 mt-1">
          Contribute authentic CAT papers to the self-growing question bank. The system extracts questions, performs 3-level deduplication, independently verifies math and logic, and promotes verified questions to the shared corpus.
        </p>
      </div>

      {msg && (
        <div
          className={`p-3 rounded text-xs border ${
            msg.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-700'
              : msg.type === 'info'
              ? 'bg-blue-50 border-blue-200 text-blue-700'
              : 'bg-red-50 border-red-200 text-red-700'
          }`}
        >
          {msg.text}
        </div>
      )}

      {/* Upload Form Card */}
      <form onSubmit={handleUpload} className="bg-white border border-gray-200 rounded p-6 space-y-5">
        <h2 className="text-sm font-semibold text-gray-900">Upload CAT Examination PDF</h2>

        <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
          <UploadCloud className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-xs text-gray-600 font-medium">
            {selectedFile ? selectedFile.name : 'Click to select or drag and drop authentic CAT PDF paper'}
          </p>
          <p className="text-[11px] text-gray-400 mt-1">PDF format with magic byte signature • Max 50MB</p>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="mt-3 text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
              Examination Year
            </label>
            <input
              type="number"
              min={2000}
              max={2025}
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:border-blue-600"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
              Slot / Administration
            </label>
            <select
              value={slot}
              onChange={(e) => setSlot(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:border-blue-600 bg-white"
            >
              <option value="Slot 1">Slot 1 (Morning)</option>
              <option value="Slot 2">Slot 2 (Afternoon)</option>
              <option value="Slot 3">Slot 3 (Evening)</option>
              <option value="Single Slot">Single Slot (Pre-2015)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
              Source Provenance
            </label>
            <input
              type="text"
              value={sourceName}
              onChange={(e) => setSourceName(e.target.value)}
              placeholder="e.g. Official IIM Lucknow release"
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:border-blue-600"
              required
            />
          </div>
        </div>

        {/* Sharing Consent & Legal Eligibility */}
        <div className="bg-blue-50/50 border border-blue-100 rounded p-4 space-y-3">
          <div className="flex items-start gap-2.5">
            <input
              type="checkbox"
              id="allowSharing"
              checked={allowSharing}
              onChange={(e) => setAllowSharing(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="allowSharing" className="text-xs text-gray-700">
              <strong className="font-semibold text-gray-900 block">
                Allow sharing verified questions to Global Question Bank
              </strong>
              If enabled, questions that pass independent verification and deduplication will be made available to every user. Your original uploaded PDF remains strictly private to your account.
            </label>
          </div>

          <div className="flex items-start gap-2.5">
            <input
              type="checkbox"
              id="termsAccepted"
              checked={termsAccepted}
              onChange={(e) => setTermsAccepted(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              required
            />
            <label htmlFor="termsAccepted" className="text-xs text-gray-700">
              <strong className="font-semibold text-gray-900 block">
                Confirm legal eligibility and authenticity
              </strong>
              I confirm this document is an authentic CAT examination paper and eligible for community educational analysis.
            </label>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={!selectedFile || uploadMutation.isPending}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors disabled:opacity-50"
          >
            {uploadMutation.isPending ? 'Validating & Uploading...' : 'Upload & Register Paper'}
          </button>
        </div>
      </form>

      {/* Uploaded Papers List */}
      <div className="bg-white border border-gray-200 rounded p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900">Your Uploaded Historical Papers</h2>
          <Link
            to="/contributions"
            className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
          >
            <History className="w-3.5 h-3.5" />
            <span>View Full Contribution Audit History</span>
          </Link>
        </div>

        {isLoading ? (
          <p className="text-xs text-gray-500 py-4 text-center">Loading imported papers...</p>
        ) : !papersData?.items.length ? (
          <div className="text-center py-8 text-gray-400 text-xs">
            No historical papers uploaded yet. Upload a CAT paper above to begin extraction.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Title / Year</th>
                  <th className="py-2.5 px-3">Slot</th>
                  <th className="py-2.5 px-3">Source Provenance</th>
                  <th className="py-2.5 px-3">Processing Status</th>
                  <th className="py-2.5 px-3">Sharing Status</th>
                  <th className="py-2.5 px-3">Questions</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {papersData.items.map((paper) => {
                  const pAny = paper as any;
                  return (
                    <tr key={paper.id} className="hover:bg-gray-50">
                      <td className="py-3 px-3 font-medium text-gray-900 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-gray-400" />
                        <span>{paper.title || `CAT ${paper.year}`}</span>
                      </td>
                      <td className="py-3 px-3 text-gray-600">{paper.slot || 'N/A'}</td>
                      <td className="py-3 px-3 text-gray-600">{paper.source}</td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium ${
                            pAny.is_duplicate
                              ? 'bg-purple-50 text-purple-700 border border-purple-200'
                              : paper.extraction_status === 'completed'
                              ? 'bg-green-50 text-green-700 border border-green-200'
                              : paper.extraction_status === 'processing'
                              ? 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                              : 'bg-gray-50 text-gray-700 border border-gray-200'
                          }`}
                        >
                          {pAny.is_duplicate ? 'Duplicate Reused' : paper.extraction_status}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium ${
                            pAny.sharing_status === 'approved'
                              ? 'bg-green-50 text-green-700'
                              : pAny.sharing_status === 'private'
                              ? 'bg-gray-100 text-gray-600'
                              : 'bg-amber-50 text-amber-700'
                          }`}
                        >
                          {pAny.sharing_status === 'approved' ? (
                            <ShieldCheck className="w-3 h-3" />
                          ) : (
                            <Lock className="w-3 h-3" />
                          )}
                          <span className="capitalize">{pAny.sharing_status || 'pending'}</span>
                        </span>
                      </td>
                      <td className="py-3 px-3 text-gray-900 font-semibold">
                        {paper.question_count || 0}
                      </td>
                      <td className="py-3 px-3 text-right">
                        {paper.extraction_status !== 'completed' && !pAny.is_duplicate && (
                          <button
                            onClick={() => handleExtract(paper.id)}
                            disabled={extractMutation.isPending}
                            className="text-blue-600 hover:text-blue-700 font-semibold text-xs flex items-center gap-1 ml-auto"
                          >
                            <RefreshCw className="w-3 h-3" />
                            <span>Extract & Verify</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
