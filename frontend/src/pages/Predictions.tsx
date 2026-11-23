import React, { useState } from 'react';
import { usePredictions } from '../hooks/usePredictions';
import { ChevronDown, ChevronUp, AlertTriangle, CheckCircle2, ShieldAlert, BarChart3 } from 'lucide-react';
import type { Prediction, PredictionEvidence } from '../types';

export const Predictions: React.FC = () => {
  const [sectionFilter, setSectionFilter] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: predictionsData, isLoading } = usePredictions(
    sectionFilter === 'ALL' ? undefined : { section: sectionFilter }
  );

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">CAT 2026 Evidence-Backed Predictions</h1>
        <p className="text-sm text-gray-500 mt-1">
          Calibrated question archetypes derived from historical pattern analysis & walk-forward backtesting.
        </p>
      </div>

      {/* Methodology & Limitations Disclosure */}
      <div className="bg-amber-50/60 border border-amber-200 rounded p-4 text-xs text-amber-800 flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-amber-900">Statistical Prediction Principles</p>
          <p className="leading-relaxed">
            Confidence levels are statistically calibrated and strictly capped at 0.89 to prevent false certainty.
            Every prediction is supported by traceable historical paper citations. Historical frequency is never treated as certainty.
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        {['ALL', 'QA', 'DILR', 'VARC'].map((sec) => (
          <button
            key={sec}
            onClick={() => setSectionFilter(sec)}
            className={`px-3 py-1.5 text-xs font-semibold rounded transition-colors ${
              sectionFilter === sec
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            {sec === 'ALL' ? 'All Sections' : sec}
          </button>
        ))}
      </div>

      {/* Predictions List */}
      {isLoading ? (
        <p className="text-xs text-gray-500 py-8 text-center">Loading calibrated predictions...</p>
      ) : !predictionsData?.length ? (
        <div className="bg-white border border-gray-200 rounded p-8 text-center text-xs text-gray-400">
          No predictions available for the selected section.
        </div>
      ) : (
        <div className="space-y-4">
          {predictionsData.map((pred: Prediction) => {
            const isExpanded = expandedId === pred.id;
            const topic = pred.topic_name || pred.topic || 'General';
            const subtopic = pred.subtopic_name || pred.subtopic;
            const archetype = pred.predicted_archetype || `${topic} Archetype`;
            const confidence = pred.calibrated_confidence ?? pred.confidence ?? 0.75;
            const explanation = pred.explanation || pred.reasoning || '';
            const evidenceList = pred.historical_evidence || pred.evidence || [];

            return (
              <div
                key={pred.id}
                className="bg-white border border-gray-200 rounded p-5 space-y-3 transition-shadow hover:shadow-xs"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                      {pred.section}
                    </span>
                    <span className="text-xs text-gray-500 font-medium">
                      {topic} {subtopic && `› ${subtopic}`}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5 text-xs">
                      <span className="text-gray-400">Calibrated Conf:</span>
                      <span className="font-semibold text-emerald-600 font-mono">
                        {Math.round(confidence * 100)}%
                      </span>
                    </div>

                    <button
                      onClick={() => toggleExpand(pred.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Archetype Title */}
                <div>
                  <h2 className="text-sm font-semibold text-gray-900">{archetype}</h2>
                  <p className="text-xs text-gray-600 mt-1 leading-relaxed">{explanation}</p>
                </div>

                {/* Expandable Evidence Drawer */}
                {isExpanded && (
                  <div className="pt-3 border-t border-gray-100 space-y-4 text-xs">
                    {/* Limitations & Uncertainty */}
                    {pred.uncertainty_and_limitations && (
                      <div className="p-3 bg-gray-50 border border-gray-200 rounded text-gray-700 flex items-start gap-2">
                        <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                        <div>
                          <p className="font-semibold text-gray-900">Uncertainty & Exam Limitations</p>
                          <p className="mt-0.5 leading-relaxed">{pred.uncertainty_and_limitations}</p>
                        </div>
                      </div>
                    )}

                    {/* Backtesting Comparison */}
                    {pred.backtesting_baseline_comparison && (
                      <div className="p-3 bg-blue-50/50 border border-blue-100 rounded text-blue-900 flex items-start gap-2">
                        <BarChart3 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                        <div>
                          <p className="font-semibold">Walk-Forward Backtesting Baseline</p>
                          <p className="mt-0.5 text-blue-800">{pred.backtesting_baseline_comparison}</p>
                        </div>
                      </div>
                    )}

                    {/* Historical Citations */}
                    <div>
                      <p className="font-semibold text-gray-800 mb-2">Historical Supporting Evidence</p>
                      <div className="space-y-2">
                        {evidenceList.map((ev: PredictionEvidence, idx: number) => (
                          <div
                            key={idx}
                            className="p-2.5 bg-blue-50/40 border border-blue-100 rounded text-gray-700 flex items-start gap-2"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                            <div>
                              <p className="font-medium text-gray-900">
                                {ev.evidence_type ? ev.evidence_type.toUpperCase().replace('_', ' ') : ev.factor || 'EVIDENCE'}
                              </p>
                              <p className="leading-relaxed mt-0.5">{ev.evidence_text || ev.description}</p>
                              {ev.reference_years && ev.reference_years.length > 0 && (
                                <p className="text-[10px] text-gray-500 mt-1">
                                  Referenced CAT Years: {ev.reference_years.join(', ')}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
