import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { ShieldCheck, LogOut, Key } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-gray-200 bg-white px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold text-sm tracking-wider">
          CAT
        </div>
        <div>
          <span className="font-semibold text-gray-900 tracking-tight">CAT Intelligence</span>
          <span className="ml-1.5 text-xs text-blue-600 font-medium px-1.5 py-0.5 bg-blue-50 border border-blue-200 rounded">
            2026
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Link
          to="/settings"
          className="flex items-center gap-1.5 text-xs font-medium text-gray-600 hover:text-blue-600 px-2.5 py-1.5 rounded border border-gray-200 hover:border-blue-300 transition-colors"
        >
          <Key className="w-3.5 h-3.5" />
          <span>BYOK Session</span>
        </Link>

        {user && (
          <div className="flex items-center gap-3 pl-3 border-l border-gray-200">
            <div className="text-right">
              <p className="text-xs font-medium text-gray-900">{user.email}</p>
              <div className="flex items-center gap-1 justify-end text-[10px] text-green-600">
                <ShieldCheck className="w-3 h-3" />
                <span>Isolated RAM</span>
              </div>
            </div>

            <button
              onClick={() => logout()}
              title="Log out and purge session keys"
              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
