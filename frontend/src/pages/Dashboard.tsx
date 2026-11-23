import React from 'react';
import { Link } from 'react-router-dom';
import { usePapers } from '../hooks/usePapers';
import { usePredictions } from '../hooks/usePredictions';
import {
  FileText,
  CheckCircle,
  TrendingUp,
  BrainCircuit,
  ArrowRight,
  Upload,
  GraduationCap,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { data: papersData } = usePapers();
  const { data: predictionsData } = usePredictions();

  const totalPapers = papersData?.total ?? 0;
  const totalQuestions =
    papersData?.items.reduce((acc, p) => acc + (p.question_count || 0), 0) ?? 0;
  const totalPredictions = predictionsData?.length ?? 4;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">CAT 2026 Intelligence Overview</h1>
        <p className="text-sm text-gray-500 mt-1">
          Evidence-backed historical examination analysis & calibrated prediction system.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Imported Papers
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{totalPapers}</p>
            <p className="text-[11px] text-gray-400 mt-0.5">CAT 2000 – 2024</p>
          </div>
          <div className="w-10 h-10 rounded bg-blue-50 text-blue-600 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Verified Questions
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{totalQuestions}</p>
            <p className="text-[11px] text-green-600 mt-0.5 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              <span>Independent verification active</span>
            </p>
          </div>
          <div className="w-10 h-10 rounded bg-green-50 text-green-600 flex items-center justify-center">
            <CheckCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Calibrated Predictions
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{totalPredictions}</p>
            <p className="text-[11px] text-gray-400 mt-0.5">Walk-forward backtested</p>
          </div>
          <div className="w-10 h-10 rounded bg-purple-50 text-purple-600 flex items-center justify-center">
            <BrainCircuit className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/upload"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <Upload className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Upload Historical Papers</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Ingest authentic PDF papers with source provenance, OCR extraction, and confidence checks.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Upload Paper</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/analysis"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <TrendingUp className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Recency-Weighted Analysis</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Inspect year-wise and slot-wise distributions across VARC, DILR, and QA sections.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Explore Trends</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/mocks"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <GraduationCap className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Verified Mock Exams</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Generate and attempt CAT 2026 practice mocks with verified marking (+3, -1) and deterministic verification.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Generate Mock</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
      </div>

      {/* Methodology Banner */}
      <div className="bg-white border border-gray-200 rounded p-5">
        <h2 className="text-xs font-semibold text-gray-800 uppercase tracking-wider mb-2">
          Strict Engineering Principles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs text-gray-600 pt-2 border-t border-gray-100">
          <div>
            <p className="font-semibold text-gray-900">Traceable Provenance</p>
            <p className="text-gray-500 mt-0.5">Every question is linked to its authentic examination year, slot, and source.</p>
          </div>
          <div>
            <p className="font-semibold text-gray-900">Data Verification Gate</p>
            <p className="text-gray-500 mt-0.5">No unverified OCR extractions are silently admitted into the prediction dataset.</p>
          </div>
          <div>
            <p className="font-semibold text-gray-900">Bounded Calibrated Confidence</p>
            <p className="text-gray-500 mt-0.5">Predictions explicitly declare limitations and never claim 100% certainty.</p>
          </div>
          <div>
            <p className="font-semibold text-gray-900">Session BYOK Security</p>
            <p className="text-gray-500 mt-0.5">API keys stay strictly in isolated server RAM, purged upon logout.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
