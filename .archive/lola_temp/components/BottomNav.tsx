import React from 'react';
import { ViewState } from '../types';

interface BottomNavProps {
  currentView: ViewState;
  onChangeView: (view: ViewState) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentView, onChangeView }) => {
  const navItems = [
    { id: ViewState.HOME, icon: 'cottage', label: 'Home' },
    { id: ViewState.PROJECTS, icon: 'folder_open', label: 'Projects' },
    { id: ViewState.PIPELINE, icon: 'add', label: 'Create', isFab: true },
    { id: ViewState.TEAM, icon: 'groups', label: 'Team' },
    { id: ViewState.SETTINGS, icon: 'settings', label: 'Settings' },
  ];

  return (
    <div className="absolute bottom-0 left-0 w-full glass-nav pb-6 pt-3 px-2 z-50">
      <div className="flex justify-between items-end relative">
        {navItems.map((item) => {
          const isActive = currentView === item.id;
          
          if (item.isFab) {
            return (
              <div key={item.id} className="relative -top-6 flex flex-1 flex-col items-center justify-end">
                <button 
                  onClick={() => onChangeView(ViewState.PIPELINE)}
                  className={`size-14 rounded-full bg-primary flex items-center justify-center shadow-[0_0_20px_rgba(182,19,236,0.6)] border-4 border-[#1d1022] transform transition-transform active:scale-95 group ${isActive ? 'ring-2 ring-white/20' : ''}`}
                >
                  <span className={`material-symbols-outlined text-white transition-transform duration-300 ${isActive ? 'rotate-45' : 'group-hover:rotate-90'}`} style={{ fontSize: '28px' }}>
                    add
                  </span>
                </button>
                <p className="text-slate-600 dark:text-white text-[10px] font-bold tracking-wide mt-1 absolute -bottom-6 opacity-0">Create</p>
              </div>
            );
          }

          return (
            <button 
              key={item.id}
              onClick={() => onChangeView(item.id as ViewState)}
              className="flex flex-1 flex-col items-center justify-end gap-1 group w-full"
            >
              <div className="relative p-1">
                <span 
                  className={`material-symbols-outlined transition-all ${isActive ? 'text-primary scale-110' : 'text-slate-400 dark:text-white/40 group-hover:text-slate-600 dark:group-hover:text-white'}`} 
                  style={{ fontSize: '26px', fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
                >
                  {item.icon}
                </span>
                {isActive && (
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></div>
                )}
              </div>
              <p className={`transition-colors text-[10px] font-medium tracking-wide mt-1 ${isActive ? 'text-slate-900 dark:text-white font-bold' : 'text-slate-400 dark:text-white/40 group-hover:text-slate-600 dark:group-hover:text-white'}`}>
                {item.label}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};