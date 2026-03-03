import React, { useState } from 'react';
import { ViewState, Project } from '../types';

interface ProjectsProps {
  onNavigate: (view: ViewState) => void;
  projects: Project[];
  onCreateProject: (name: string, color: string) => void;
  onSelectProject: (id: string) => void;
}

export const Projects: React.FC<ProjectsProps> = ({ onNavigate, projects, onCreateProject, onSelectProject }) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [selectedColor, setSelectedColor] = useState('bg-primary');

  const colors = [
    'bg-primary', 'bg-blue-500', 'bg-green-500', 'bg-orange-500', 'bg-red-500', 'bg-teal-500'
  ];

  const handleCreate = () => {
    if (newProjectName.trim()) {
        onCreateProject(newProjectName, selectedColor);
        setNewProjectName('');
        setIsCreating(false);
    }
  };

  const formatTime = (timestamp: number) => {
    const diff = Date.now() - timestamp;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  return (
    <div className="flex-1 overflow-y-auto no-scrollbar pb-24 px-4 pt-8 relative">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-white text-2xl font-bold tracking-tight">Projects</h1>
        <button 
            onClick={() => setIsCreating(true)}
            className="flex items-center justify-center size-10 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
        >
            <span className="material-symbols-outlined text-white">add</span>
        </button>
      </div>

      {/* Create Project Modal Overlay */}
      {isCreating && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={() => setIsCreating(false)}>
            <div className="bg-surface-dark border border-white/10 rounded-2xl p-6 w-full max-w-sm shadow-2xl" onClick={e => e.stopPropagation()}>
                <h3 className="text-white font-bold text-lg mb-4">New Project</h3>
                <input 
                    type="text" 
                    placeholder="Project Name (e.g. Summer 2025)"
                    value={newProjectName}
                    onChange={e => setNewProjectName(e.target.value)}
                    autoFocus
                    className="w-full bg-background-dark border border-white/10 rounded-lg p-3 text-white mb-4 focus:ring-1 focus:ring-primary focus:border-primary outline-none"
                    onKeyDown={e => e.key === 'Enter' && handleCreate()}
                />
                <div className="flex gap-2 mb-6 justify-between">
                    {colors.map(c => (
                        <button 
                            key={c}
                            onClick={() => setSelectedColor(c)}
                            className={`size-8 rounded-full ${c} ${selectedColor === c ? 'ring-2 ring-white ring-offset-2 ring-offset-surface-dark' : 'opacity-60 hover:opacity-100'} transition-all`}
                        />
                    ))}
                </div>
                <div className="flex gap-3">
                    <button 
                        onClick={() => setIsCreating(false)}
                        className="flex-1 py-3 rounded-xl font-medium text-white/60 hover:bg-white/5 transition-colors"
                    >
                        Cancel
                    </button>
                    <button 
                        onClick={handleCreate}
                        disabled={!newProjectName.trim()}
                        className="flex-1 py-3 rounded-xl font-bold bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50"
                    >
                        Create
                    </button>
                </div>
            </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {projects.map((project) => (
            <div 
                key={project.id} 
                className="group bg-surface-dark border border-white/5 rounded-xl p-4 flex items-center gap-4 hover:bg-white/5 transition-colors cursor-pointer"
                onClick={() => onSelectProject(project.id)}
            >
                <div className={`size-12 rounded-lg ${project.color} bg-opacity-20 flex items-center justify-center text-white font-bold text-lg shadow-[0_0_15px_rgba(0,0,0,0.2)]`}>
                    {project.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                    <h3 className="text-white font-bold text-base">{project.name}</h3>
                    <p className="text-white/40 text-xs">{project.assetCount} assets • Last edited {formatTime(project.lastEdited)}</p>
                </div>
                <span className="material-symbols-outlined text-white/20 group-hover:text-white/60 transition-colors">chevron_right</span>
            </div>
        ))}
        
        <div 
            onClick={() => setIsCreating(true)}
            className="bg-surface-dark border border-dashed border-white/10 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:bg-white/5 transition-colors cursor-pointer group"
        >
            <div className="size-10 rounded-full bg-white/5 group-hover:bg-primary/20 flex items-center justify-center mb-2 transition-colors">
                <span className="material-symbols-outlined text-white/40 group-hover:text-primary">folder_open</span>
            </div>
            <p className="text-white/60 text-sm font-medium">Create New Project</p>
        </div>
      </div>
    </div>
  );
};