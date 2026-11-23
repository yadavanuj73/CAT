import React, { useState, useEffect } from 'react';
import { apiKeysApi } from '../services/api';
import type { ApiKeyStatus } from '../types';
import { Key, CheckCircle, Trash2, ShieldCheck, Lock } from 'lucide-react';

export const Settings: React.FC = () => {
  const [apiKey, setApiKey] = useState('');
  const [mode, setMode] = useState<'session' | 'save'>('session');
  const [status, setStatus] = useState<ApiKeyStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchStatus = async () => {
    try {
      const data = await apiKeysApi.getKeyStatus();
      if (data && data.length > 0) {
        setStatus(data[0]);
      }
    } catch {
      // Ignored
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleSetKey = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = apiKey.trim();
    if (!trimmed.startsWith('AIza') && !trimmed.startsWith('sk-') && trimmed.length < 20) {
      setMessage({
        type: 'error',
        text: 'API key must start with AIza (Gemini) or sk- (OpenAI), or be at least 20 characters.',
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const provider = trimmed.startsWith('sk-') ? 'openai' : 'gemini';
      if (mode === 'session') {
        await apiKeysApi.setSessionKey({ provider, api_key: trimmed });
        setMessage({
          type: 'success',
          text: `API key saved strictly in session RAM (${provider.toUpperCase()}). Cleared automatically upon logout.`,
        });
      } else {
        await apiKeysApi.saveKey({ provider, api_key: trimmed, save: true });
        setMessage({
          type: 'success',
          text: `API key encrypted with AES-256-GCM and saved (${provider.toUpperCase()}).`,
        });
      }
      setApiKey('');
      fetchStatus();
    } catch (err: unknown) {
      const errorMsg =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        'Failed to set API key.';
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await apiKeysApi.deleteKey(status?.provider || 'gemini');
      setStatus(null);
      setMessage({ type: 'success', text: 'API credentials permanently purged.' });
      fetchStatus();
    } catch {
      setMessage({ type: 'error', text: 'Failed to purge key.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">API Key Security (BYOK)</h1>
        <p className="text-sm text-gray-500 mt-1">
          Bring Your Own Key architecture. Your credentials are never logged, leaked, or exposed.
        </p>
      </div>

      {message && (
        <div
          className={`p-3.5 rounded text-xs border ${
            message.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-700'
              : 'bg-red-50 border-red-200 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Key Status Card */}
      <div className="bg-white border border-gray-200 rounded p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-gray-500" />
            <h2 className="text-sm font-semibold text-gray-900">Current Key Status</h2>
          </div>
          {status?.is_set ? (
            <span className="flex items-center gap-1.5 text-xs text-green-600 bg-green-50 border border-green-200 px-2.5 py-0.5 rounded font-medium">
              <CheckCircle className="w-3.5 h-3.5" />
              Active ({status.is_saved ? 'AES-256 Encrypted' : 'Session RAM Only'})
            </span>
          ) : (
            <span className="text-xs text-gray-400 bg-gray-50 border border-gray-200 px-2.5 py-0.5 rounded">
              Not Configured
            </span>
          )}
        </div>

        {status?.is_set && (
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <span className="text-xs text-gray-600 font-mono">
              Key Mask: {status.masked_key}
            </span>
            <button
              onClick={handleDelete}
              disabled={loading}
              className="flex items-center gap-1 text-xs text-red-600 hover:text-red-700 hover:underline"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Purge Credential</span>
            </button>
          </div>
        )}
      </div>

      {/* Configuration Form */}
      <div className="bg-white border border-gray-200 rounded p-5 space-y-4">
        <h2 className="text-sm font-semibold text-gray-900">Configure AI Provider Key (Google Gemini / OpenAI)</h2>

        {/* Mode selector */}
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setMode('session')}
            className={`p-3 text-left border rounded transition-colors ${
              mode === 'session'
                ? 'border-blue-600 bg-blue-50/50 ring-1 ring-blue-600'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-900 mb-1">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>Session-Only RAM (Default)</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-relaxed">
              Key resides only in volatile server memory. Automatically expunged on logout,
              expiry, or server restart.
            </p>
          </button>

          <button
            type="button"
            onClick={() => setMode('save')}
            className={`p-3 text-left border rounded transition-colors ${
              mode === 'save'
                ? 'border-blue-600 bg-blue-50/50 ring-1 ring-blue-600'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-900 mb-1">
              <Lock className="w-4 h-4 text-blue-600" />
              <span>Encrypted Persistence (Opt-in)</span>
            </div>
            <p className="text-[11px] text-gray-500 leading-relaxed">
              Encrypted using AES-256-GCM with master encryption key. Persists across restarts.
            </p>
          </button>
        </div>

        <form onSubmit={handleSetKey} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
              Google Gemini / OpenAI Secret API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIzaSy... or sk-..."
              className="w-full px-3 py-2 text-sm font-mono border border-gray-200 rounded focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
              required
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className="text-[11px] text-gray-400">
              Keys are never returned to client JavaScript or written to logs.
            </span>
            <button
              type="submit"
              disabled={loading || !apiKey}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors disabled:opacity-50"
            >
              {loading ? 'Validating...' : mode === 'session' ? 'Set Session Key' : 'Encrypt & Save Key'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
