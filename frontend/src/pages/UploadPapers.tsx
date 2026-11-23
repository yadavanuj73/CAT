import React, { useState } from 'react';
import { usePapers, useUploadPaper, useExtractPaper } from '../hooks/usePapers';
import { UploadCloud, FileText, RefreshCw } from 'lucide-react';

export const UploadPapers: React.FC = () => {
  const { data: papersData, isLoading } = usePapers();
  const uploadMutation = useUploadPaper();
  const extractMutation = useExtractPaper();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [year, setYear] = useState<number>(2024);
  const [slot, setSlot] = useState<string>('Slot 1');
  const [sourceName, setSourceName] = useState<string>('IIM Official');
  const [sourceType] = useState<string>('official');
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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

    setMsg(null);
    try {
      await uploadMutation.mutateAsync({
        file: selectedFile,
        metadata: {
          title: `CAT ${year} ${slot}`,
          year,
          slot,
          source: sourceType,
        },
      });
      setMsg({ type: 'success', text: `Paper uploaded with SHA-256 provenance tracking.` });
      setSelectedFile(null);
    } catch {
      setMsg({ type: 'error', text: 'Failed to upload paper. Please check file format.' });
    }
  };

  const handleExtract = async (paperId: string) => {
    try {
      await extractMutation.mutateAsync(paperId);
      setMsg({ type: 'success', text: 'Questions extracted successfully and queued for verification.' });
    } catch {
      setMsg({ type: 'error', text: 'Extraction failed.' });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">Upload Authentic Historical Papers</h1>
        <p className="text-sm text-gray-500 mt-1">
          Import original CAT papers from 2000–2025. Preserves provenance, tables, and passage text.
        </p>
      </div>

      {msg && (
        <div
          className={`p-3 rounded text-xs border ${
            msg.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-700'
              : 'bg-red-50 border-red-200 text-red-700'
          }`}
        >
          {msg.text}
        </div>
      )}

      {/* Upload Form Card */}
      <form onSubmit={handleUpload} className="bg-white border border-gray-200 rounded p-6 space-y-5">
        <h2 className="text-sm font-semibold text-gray-900">Upload PDF Paper</h2>

        <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
          <UploadCloud className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-xs text-gray-600 font-medium">
            {selectedFile ? selectedFile.name : 'Click to select or drag and drop authentic CAT PDF paper'}
          </p>
          <p className="text-[11px] text-gray-400 mt-1">Maximum file size: 50MB</p>
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

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={!selectedFile || uploadMutation.isPending}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors disabled:opacity-50"
          >
            {uploadMutation.isPending ? 'Uploading & Verifying...' : 'Upload & Register Paper'}
          </button>
        </div>
      </form>

      {/* Uploaded Papers List */}
      <div className="bg-white border border-gray-200 rounded p-6 space-y-4">
        <h2 className="text-sm font-semibold text-gray-900">Imported Historical Papers</h2>

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
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Questions</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {papersData.items.map((paper) => (
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
                          paper.extraction_status === 'completed'
                            ? 'bg-green-50 text-green-700 border border-green-200'
                            : paper.extraction_status === 'processing'
                            ? 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                            : 'bg-gray-50 text-gray-700 border border-gray-200'
                        }`}
                      >
                        {paper.extraction_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-gray-900 font-semibold">
                      {paper.question_count || 0}
                    </td>
                    <td className="py-3 px-3 text-right">
                      {paper.extraction_status !== 'completed' && (
                        <button
                          onClick={() => handleExtract(paper.id)}
                          disabled={extractMutation.isPending}
                          className="text-blue-600 hover:text-blue-700 font-semibold text-xs flex items-center gap-1 ml-auto"
                        >
                          <RefreshCw className="w-3 h-3" />
                          <span>Extract Questions</span>
                        </button>
                      )}
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
};
