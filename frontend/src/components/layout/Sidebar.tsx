import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UploadCloud,
  LineChart,
  BrainCircuit,
  GraduationCap,
  Settings,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/upload', label: 'Upload PYQs', icon: UploadCloud },
  { to: '/analysis', label: 'Paper Analysis', icon: LineChart },
  { to: '/predictions', label: 'CAT 2026 Predictions', icon: BrainCircuit },
  { to: '/mocks', label: 'Mock Tests', icon: GraduationCap },
  { to: '/settings', label: 'BYOK & Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-gray-200 bg-white flex flex-col justify-between shrink-0 h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-gray-400 uppercase">
          Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold border-l-2 border-blue-600 rounded-l-none'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 border-t border-gray-100 text-[11px] text-gray-400 space-y-1">
        <p className="font-medium text-gray-500">Rigorous CAT Verification</p>
        <p>100% verified historical citations. No fabricated predictions.</p>
      </div>
    </aside>
  );
};
