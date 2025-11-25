import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Camera, Map as MapIcon, History, Bell, Leaf } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const SidebarLink = ({ to, icon: Icon, label }: { to: string; icon: any; label: string }) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
          isActive
            ? 'bg-green-600 text-white shadow-lg shadow-green-900/20'
            : 'text-slate-400 hover:bg-slate-800 hover:text-green-400'
        }`
      }
    >
      <Icon className="w-5 h-5" />
      <span className="font-medium">{label}</span>
    </NavLink>
  );
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col hidden md:flex z-50">
        <div className="p-6 flex items-center gap-3 border-b border-slate-800">
          <div className="bg-green-500 p-2 rounded-lg">
            <Leaf className="w-6 h-6 text-slate-900" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-green-400 to-emerald-600 bg-clip-text text-transparent">
              EcoDetect
            </h1>
            <p className="text-xs text-slate-500">Waste AI Analysis</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2 mt-4">
          <SidebarLink to="/" icon={Camera} label="Live Scanner" />
          <SidebarLink to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
          <SidebarLink to="/map" icon={MapIcon} label="Live Map" />
          <SidebarLink to="/history" icon={History} label="History" />
          <SidebarLink to="/alerts" icon={Bell} label="Alerts" />
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-800/50 rounded-lg p-3 text-xs text-slate-400 text-center">
            <p>System Status: <span className="text-green-400 font-bold">Online</span></p>
            <p className="mt-1 opacity-50">v1.2.0 • YOLO11 + Gemini</p>
          </div>
        </div>
      </aside>

      {/* Mobile Header (Visible only on small screens) */}
      <div className="md:hidden fixed top-0 w-full bg-slate-900 border-b border-slate-800 z-50 p-4 flex justify-between items-center">
         <div className="flex items-center gap-2">
            <Leaf className="w-6 h-6 text-green-500" />
            <span className="font-bold text-lg">EcoDetect</span>
         </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-auto relative md:static mt-16 md:mt-0">
        <div className="max-w-7xl mx-auto p-4 md:p-8 space-y-8">
            {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;