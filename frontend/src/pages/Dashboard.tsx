import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { usePapers } from '../hooks/usePapers';
import { sharedApi } from '../services/api';
import type { SharedCorpusStats } from '../types';
import {
  FileText,
  CheckCircle,
  TrendingUp,
  BrainCircuit,
  ArrowRight,
  Upload,
  GraduationCap,
  Database,
  History,
  Layers,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { data: papersData } = usePapers();
  const [sharedStats, setSharedStats] = useState<SharedCorpusStats | null>(null);

  useEffect(() => {
    sharedApi.getStats().then(setSharedStats).catch(() => {});
  }, []);

  const totalUserPapers = papersData?.total ?? 0;
  const verifiedSharedPapers = sharedStats?.total_verified_papers ?? 0;
  const uniqueSharedQuestions = sharedStats?.total_unique_verified_questions ?? 0;
  const duplicatesPrevented = sharedStats?.total_duplicates_prevented ?? 0;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">CAT Intelligence 2026 Platform Overview</h1>
        <p className="text-sm text-gray-500 mt-1">
          Self-growing AI examination intelligence platform with database-level deduplication, authentic historical pattern analysis, independent verification gates, and session-first BYOK privacy.
        </p>
      </div>

      {/* Global Shared Knowledge Base Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Shared Verified Papers
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{verifiedSharedPapers}</p>
            <p className="text-[11px] text-gray-400 mt-0.5">CAT 2000 – 2025 corpus</p>
          </div>
          <div className="w-10 h-10 rounded bg-blue-50 text-blue-600 flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Unique Verified Questions
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{uniqueSharedQuestions}</p>
            <p className="text-[11px] text-green-600 mt-0.5 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              <span>Available to all users</span>
            </p>
          </div>
          <div className="w-10 h-10 rounded bg-green-50 text-green-600 flex items-center justify-center">
            <CheckCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Duplicates Prevented
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{duplicatesPrevented}</p>
            <p className="text-[11px] text-purple-600 mt-0.5">DB-level uniqueness</p>
          </div>
          <div className="w-10 h-10 rounded bg-purple-50 text-purple-600 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Your Uploaded Papers
            </p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{totalUserPapers}</p>
            <p className="text-[11px] text-gray-400 mt-0.5">Private uploads & logs</p>
          </div>
          <div className="w-10 h-10 rounded bg-amber-50 text-amber-600 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Quick Action Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/upload"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <Upload className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Upload & Contribute Papers</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Ingest authentic PDF papers with SHA-256 fingerprinting, automated deduplication, and sharing consent.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Upload Paper</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/shared-bank"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <Database className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Shared Question Bank</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Browse community-contributed and verified CAT questions with multi-source examination provenance.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Browse Question Bank</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/contributions"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <History className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">My Contribution History</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Inspect step-by-step extraction logs, verification statuses, rejected items, and promoted questions.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>View Processing Logs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              Analyze historical question frequencies and topic shifts across VARC, DILR, and QA using the shared corpus.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Explore Trends</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/predictions"
          className="bg-white border border-gray-200 hover:border-blue-400 rounded p-5 transition-colors group flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded bg-gray-50 group-hover:bg-blue-50 text-gray-600 group-hover:text-blue-600 flex items-center justify-center mb-3">
              <BrainCircuit className="w-4 h-4" />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">CAT 2026 Predictions</h2>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">
              Calibrated topic predictions with genuine walk-forward backtesting metrics. No fabricated percentages.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>View Predictions</span>
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
              Generate full or sectional practice mocks from shared verified questions with authentic marking scheme.
            </p>
          </div>
          <div className="flex items-center gap-1 text-xs text-blue-600 font-medium mt-4">
            <span>Start Practice Mock</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
      </div>

      {/* Architecture & Engineering Standards Banner */}
      <div className="bg-white border border-gray-200 rounded p-5">
        <h2 className="text-xs font-semibold text-gray-800 uppercase tracking-wider mb-2">
          Platform Engineering Architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs text-gray-600 pt-2 border-t border-gray-100">
          <div>
            <p className="font-semibold text-gray-900">Three-Level Deduplication</p>
            <p className="text-gray-500 mt-0.5">Level 1 (PDF SHA-256), Level 2 (Canonical question fingerprint), Level 3 (Semantic review queue).</p>
          </div>
          <div>
            <p className="font-semibold text-gray-900">Multi-Source Provenance</p>
            <p className="text-gray-500 mt-0.5">Identical questions appearing in multiple exams are stored once and linked via source mapping.</p>
          </div>
          <div>
            <p className="font-semibold text-gray-900">Multi-Stage Verification Gate</p>
            <p className="text-gray-500 mt-0.5">Only verified, non-duplicate content with explicit user consent enters the shared corpus.</p>
          </div>
          <div>
            <p className="font-semibold text-gray-900">Session BYOK Security</p>
            <p className="text-gray-500 mt-0.5">Private uploads and processing logs remain isolated. API keys stay exclusively in ephemeral RAM.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
