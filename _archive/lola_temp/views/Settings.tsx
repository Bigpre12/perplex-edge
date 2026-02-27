import React, { useState, useEffect } from 'react';

export const Settings: React.FC = () => {
  // Initialize state from localStorage or default to true (Dark Mode is default in HTML)
  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem('lola_notifications');
    return saved !== 'false'; // Default to true
  });
  
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('lola_theme');
    // If no saved preference, check if html has 'dark' class (it does by default)
    if (saved === null) return document.documentElement.classList.contains('dark');
    return saved === 'dark';
  });
  
  const [showToast, setShowToast] = useState<{message: string, type: 'success' | 'info'} | null>(null);

  // Apply Theme Side Effect
  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
      localStorage.setItem('lola_theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('lola_theme', 'light');
    }
  }, [darkMode]);

  // Save Notifications Side Effect
  useEffect(() => {
    localStorage.setItem('lola_notifications', String(notifications));
  }, [notifications]);

  const handleToast = (message: string, type: 'success' | 'info' = 'info') => {
    setShowToast({ message, type });
    setTimeout(() => setShowToast(null), 3000);
  };

  const handleLogout = () => {
     handleToast("Logging out...", 'info');
     // Simulate logout delay
     setTimeout(() => {
        window.location.reload();
     }, 1500);
  }

  return (
    <div className="flex-1 overflow-y-auto no-scrollbar pb-24 px-4 pt-8 relative">
       {/* Toast */}
      <div className={`fixed top-24 left-1/2 -translate-x-1/2 z-[60] transition-all duration-300 transform ${showToast ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0 pointer-events-none'}`}>
        {showToast && (
            <div className="bg-surface-darker border border-white/10 text-white px-4 py-2 rounded-full shadow-xl flex items-center gap-2">
            <span className={`material-symbols-outlined text-sm ${showToast.type === 'success' ? 'text-green-500' : 'text-primary'}`}>
                {showToast.type === 'success' ? 'check_circle' : 'info'}
            </span>
            <span className="text-sm font-medium">{showToast.message}</span>
            </div>
        )}
      </div>

      <h1 className="text-slate-900 dark:text-white text-2xl font-bold tracking-tight mb-6">Settings</h1>

      <div className="space-y-6">
        
        <section>
            <h2 className="text-xs font-bold text-slate-500 dark:text-white/40 uppercase tracking-wider mb-3 ml-1">Account</h2>
            <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/5 rounded-xl overflow-hidden shadow-sm dark:shadow-none">
                <div 
                    onClick={() => handleToast('Profile details updated')}
                    className="p-4 flex items-center gap-4 border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer transition-colors"
                >
                    <div className="size-8 rounded-full bg-slate-100 dark:bg-white/10 flex items-center justify-center">
                        <span className="material-symbols-outlined text-slate-600 dark:text-white text-lg">person</span>
                    </div>
                    <div className="flex-1">
                        <p className="text-slate-900 dark:text-white font-medium text-sm">Profile</p>
                        <p className="text-slate-500 dark:text-white/40 text-xs">Manage your personal info</p>
                    </div>
                    <span className="material-symbols-outlined text-slate-400 dark:text-white/20">chevron_right</span>
                </div>
                <div 
                    onClick={() => handleToast('Billing portal opened')}
                    className="p-4 flex items-center gap-4 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer transition-colors"
                >
                    <div className="size-8 rounded-full bg-slate-100 dark:bg-white/10 flex items-center justify-center">
                        <span className="material-symbols-outlined text-slate-600 dark:text-white text-lg">credit_card</span>
                    </div>
                    <div className="flex-1">
                        <p className="text-slate-900 dark:text-white font-medium text-sm">Billing</p>
                        <p className="text-slate-500 dark:text-white/40 text-xs">Active • Free Plan</p>
                    </div>
                    <span className="material-symbols-outlined text-slate-400 dark:text-white/20">chevron_right</span>
                </div>
            </div>
        </section>

        <section>
            <h2 className="text-xs font-bold text-slate-500 dark:text-white/40 uppercase tracking-wider mb-3 ml-1">App Settings</h2>
            <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/5 rounded-xl overflow-hidden shadow-sm dark:shadow-none">
                <div 
                    className="p-4 flex items-center justify-between border-b border-slate-100 dark:border-white/5 cursor-pointer hover:bg-slate-50 dark:hover:bg-white/5 transition-colors"
                    onClick={() => setNotifications(!notifications)}
                >
                    <div className="flex items-center gap-3">
                         <span className={`material-symbols-outlined ${notifications ? 'text-primary' : 'text-slate-400 dark:text-white/60'}`}>notifications</span>
                         <span className="text-slate-900 dark:text-white text-sm font-medium">Notifications</span>
                    </div>
                    <div className={`w-10 h-6 rounded-full relative transition-colors duration-300 ${notifications ? 'bg-primary' : 'bg-slate-300 dark:bg-white/20'}`}>
                        <div className={`absolute top-1 size-4 bg-white rounded-full transition-transform duration-300 ${notifications ? 'left-[1.35rem]' : 'left-1'}`}></div>
                    </div>
                </div>
                <div 
                    className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 dark:hover:bg-white/5 transition-colors"
                    onClick={() => setDarkMode(!darkMode)}
                >
                    <div className="flex items-center gap-3">
                         <span className={`material-symbols-outlined ${darkMode ? 'text-primary' : 'text-slate-400 dark:text-white/60'}`}>dark_mode</span>
                         <span className="text-slate-900 dark:text-white text-sm font-medium">Dark Mode</span>
                    </div>
                    <div className={`w-10 h-6 rounded-full relative transition-colors duration-300 ${darkMode ? 'bg-primary' : 'bg-slate-300 dark:bg-white/20'}`}>
                        <div className={`absolute top-1 size-4 bg-white rounded-full transition-transform duration-300 ${darkMode ? 'left-[1.35rem]' : 'left-1'}`}></div>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <div className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/5 rounded-xl overflow-hidden group shadow-sm dark:shadow-none">
                <div 
                    onClick={handleLogout}
                    className="p-4 flex items-center gap-3 text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 cursor-pointer transition-colors"
                >
                    <span className="material-symbols-outlined">logout</span>
                    <span className="font-medium text-sm">Log Out</span>
                </div>
            </div>
            <p className="text-center text-slate-400 dark:text-white/20 text-xs mt-6">Version 1.0.4 • LOLA AI</p>
        </section>

      </div>
    </div>
  );
};