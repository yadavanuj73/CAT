import React, { useEffect, useState } from 'react';
import { papersApi } from '../services/api';
import type { Paper, PaperContributionSummary, UserProcessingHistoryItem } from '../types';
import {
  History,
  FileText,
  Clock,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react';

export const ContributionHistory: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPaperId, setSelectedPaperId] = useState<string | null>(null);
  const [summary, setSummary] = useState<PaperContributionSummary | null>(null);
  const [historyLogs, setHistoryLogs] = useState<UserProcessingHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);

  useEffect(() => {
    loadUserPapers();
  }, []);

  const loadUserPapers = async () => {
    setIsLoading(true);
    try {
      const res = await papersApi.list();
      setPapers(res.items || []);
      if (res.items && res.items.length > 0) {
        selectPaper(res.items[0].id);
      }
    } catch (err) {
      console.error('Failed to load user papers', err);
    } finally {
      setIsLoading(false);
    }
  };

  const selectPaper = async (paperId: string) => {
    setSelectedPaperId(paperId);
    setIsDetailLoading(true);
    try {
      const [sumData, histData] = await Promise.all([
        papersApi.getSummary(paperId),
        papersApi.getHistory(paperId),
      ]);
      setSummary(sumData);
      setHistoryLogs(histData);
    } catch (err) {
      console.error('Failed to load paper details', err);
    } finally {
      setIsDetailLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            My Contribution History & Audit Logs
          </h1>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Track the lifecycle of your uploaded CAT papers: validation, extraction, independent verification, duplicate prevention, and approved contributions to the global shared question bank.
        </p>
      </div>

      {isLoading ? (
        <div className="bg-white border border-gray-200 rounded p-8 text-center text-xs text-gray-400">
          Loading contribution history...
        </div>
      ) : papers.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded p-8 text-center text-xs text-gray-400 space-y-2">
          <FileText className="w-6 h-6 text-gray-300 mx-auto" />
          <p className="font-medium text-gray-600">No papers uploaded yet in your account.</p>
          <p>Upload a CAT paper to view detailed step-by-step processing history.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Papers List (Left Column) */}
          <div className="bg-white border border-gray-200 rounded p-4 space-y-3">
            <h2 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Your Uploaded Papers ({papers.length})
            </h2>
            <div className="divide-y divide-gray-100">
              {papers.map((p) => {
                const isSelected = selectedPaperId === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => selectPaper(p.id)}
                    className={`w-full text-left p-3 rounded transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-blue-50 text-blue-900 font-semibold border-l-2 border-blue-600'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="text-xs font-medium flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-gray-400" />
                        <span>CAT {p.year} {p.slot || ''}</span>
                      </div>
                      <div className="text-[11px] text-gray-400">
                        {p.source || 'Official'} • {new Date(p.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-300" />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Details & Processing Logs (Right Column) */}
          <div className="lg:col-span-2 space-y-4">
            {isDetailLoading || !summary ? (
              <div className="bg-white border border-gray-200 rounded p-8 text-center text-xs text-gray-400">
                Loading paper contribution metrics...
              </div>
            ) : (
              <>
                {/* Contribution Metrics Cards */}
                <div className="bg-white border border-gray-200 rounded p-5 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3">
                    <div>
                      <h3 className="text-sm font-bold text-gray-900">
                        CAT {summary.year} {summary.slot || ''}
                      </h3>
                      <p className="text-[11px] text-gray-400">
                        Paper ID: <span className="font-mono">{summary.paper_id}</span>
                      </p>
                    </div>
                    <div>
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-semibold ${
                          summary.sharing_status === 'approved'
                            ? 'bg-green-50 text-green-700 border border-green-200'
                            : summary.sharing_status === 'private'
                            ? 'bg-gray-50 text-gray-700 border border-gray-200'
                            : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                        }`}
                      >
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>
                          {summary.sharing_status === 'approved'
                            ? 'Promoted to Shared Bank'
                            : summary.sharing_status === 'private'
                            ? 'Private Upload'
                            : 'Pending Verification'}
                        </span>
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="bg-gray-50 rounded p-3">
                      <div className="text-[11px] text-gray-500 font-medium">Extracted</div>
                      <div className="text-xl font-bold text-gray-900 mt-1">
                        {summary.total_extracted}
                      </div>
                    </div>
                    <div className="bg-green-50/50 rounded p-3">
                      <div className="text-[11px] text-green-700 font-medium">Verified</div>
                      <div className="text-xl font-bold text-green-800 mt-1">
                        {summary.total_verified}
                      </div>
                    </div>
                    <div className="bg-purple-50/50 rounded p-3">
                      <div className="text-[11px] text-purple-700 font-medium">Duplicates Deduplicated</div>
                      <div className="text-xl font-bold text-purple-800 mt-1">
                        {summary.total_duplicate}
                      </div>
                    </div>
                    <div className="bg-blue-50/50 rounded p-3">
                      <div className="text-[11px] text-blue-700 font-medium">Added to Global Bank</div>
                      <div className="text-xl font-bold text-blue-800 mt-1">
                        {summary.promoted_to_shared}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Processing Step-by-Step History */}
                <div className="bg-white border border-gray-200 rounded p-5 space-y-4">
                  <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-gray-400" />
                    <span>Processing Audit Trail</span>
                  </h3>

                  {historyLogs.length === 0 ? (
                    <p className="text-xs text-gray-400 py-3">No processing events recorded yet.</p>
                  ) : (
                    <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
                      {historyLogs.map((log) => (
                        <div key={log.id} className="relative">
                          <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-blue-600 border-2 border-white" />
                          <div className="text-xs font-semibold text-gray-900 flex items-center gap-2">
                            <span className="capitalize">{log.stage.replace(/_/g, ' ')}</span>
                            <span
                              className={`text-[10px] px-1.5 py-0.2 rounded font-normal uppercase ${
                                log.status === 'completed'
                                  ? 'bg-green-100 text-green-800'
                                  : log.status === 'duplicate_detected'
                                  ? 'bg-purple-100 text-purple-800'
                                  : 'bg-gray-100 text-gray-700'
                              }`}
                            >
                              {log.status.replace(/_/g, ' ')}
                            </span>
                            <span className="text-[10px] text-gray-400 ml-auto font-normal">
                              {new Date(log.created_at).toLocaleTimeString()}
                            </span>
                          </div>
                          {log.details && (
                            <div className="mt-1 bg-gray-50 rounded p-2 text-[11px] font-mono text-gray-600">
                              {JSON.stringify(log.details, null, 2)}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
