import React, { useState, useEffect } from 'react';
import { Home } from './views/Home';
import { Pipeline } from './views/Pipeline';
import { Results } from './views/Results';
import { Projects } from './views/Projects';
import { Team } from './views/Team';
import { Settings } from './views/Settings';
import { BottomNav } from './components/BottomNav';
import { ViewState, GeneratedAsset, AspectRatio, Project } from './types';

// Mock data for initial results view if navigated to directly
const MOCK_ASSETS: GeneratedAsset[] = [
  {
    id: '1',
    url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBwYCvtXp0Bf5vPTkU6jbbWYsWGG2NKfTWTVLzBLuOjkdd3pa3FFq4L6_uqFOzIgKSZ_HzeVW_axRuxc9_KTLXV5FupNv_5FEbX5tzrFs4JJnqf2j1vKFThuIGc8rziJylAVW4YWEB_YWoIg2AdDKtihxSIBw4V1l-Jxyf5Hrz8_KyqdFRiNMNQSYJRLsWB90yHkIY_WUrqABYr_08WG8kS61PNolWi8xCOibcpjsCoF_kneltHDEhV35z_x8OQfFlfF545EDoNH0w',
    type: 'image',
    aspectRatio: '9:16',
    createdAt: Date.now(),
    prompt: 'Neon fashion portrait',
    status: 'completed',
    projectId: '1' // Summer Campaign
  },
  {
    id: '2',
    url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC0vg5Gn6wgjYh8odSgFma8dT0ujBxFj51EBEZJX1tyTBR5gUoB840fw9k3ASZiDQXFXhuraaCUPz5fm2euGEA2SqKWgFxWnEpNm25jKAxVZ515jOyNSZHwPAyboAmJyE2TH7Z2CvGLKWqOywQNs3ljZd5I1oNOsoOuBVdI2zJXT-B1EW0yOjV48-QoIT_7SHAvO1p9UnVAiWjsq2NyNgef1rFJSKn2V-cv1a0DZW-A-kFmtKRz5HZbSaduCAlSirRvSw9iF47pbxI',
    type: 'image',
    aspectRatio: '1:1',
    createdAt: Date.now(),
    prompt: 'Abstract 3D shapes purple',
    status: 'completed',
    projectId: '2' // Black Friday
  },
  {
    id: '3',
    url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBOdYBC_glQTjEqWCgxt7CROLFIf2i2QP_ZbrwT9uOoA7G34T7jcWKofn-c4MBvD_jDn9z4rwtAExlCLDmuwZRgUXfT_H2fLZN14NTpF3qOB9vqVzVrGHR9yGGY04Uj1XwPp-2OKkHkfAWXfmDvfAvWhMvo7QWPWLgEjFjysKvYBSUMmWcXBcWt8ioymzSNK9dOwv2LHmNLnmgpngAegeFdMOHvTcTAuxSwycXveMvnqTi-y7RsBDY0yySDYnFl-atYIcGrf0bLW1A',
    type: 'image',
    aspectRatio: '4:5',
    createdAt: Date.now(),
    prompt: 'Cyberpunk street scene',
    status: 'completed',
    projectId: '3' // Social Q1
  }
];

const MOCK_PROJECTS: Project[] = [
  { id: '1', name: 'Summer Campaign', assetCount: 12, lastEdited: Date.now() - 7200000, color: 'bg-orange-500' },
  { id: '2', name: 'Black Friday 2024', assetCount: 45, lastEdited: Date.now() - 86400000, color: 'bg-primary' },
  { id: '3', name: 'Social Q1', assetCount: 8, lastEdited: Date.now() - 259200000, color: 'bg-blue-500' },
];

export default function App() {
  const [currentView, setCurrentView] = useState<ViewState>(ViewState.HOME);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  
  // Load state from localStorage or use mock data
  const [results, setResults] = useState<GeneratedAsset[]>(() => {
    try {
      const saved = localStorage.getItem('lola_assets');
      return saved ? JSON.parse(saved) : MOCK_ASSETS;
    } catch (e) {
      console.error("Failed to load assets from storage", e);
      return MOCK_ASSETS;
    }
  });

  const [projects, setProjects] = useState<Project[]>(() => {
    try {
        const saved = localStorage.getItem('lola_projects');
        return saved ? JSON.parse(saved) : MOCK_PROJECTS;
    } catch (e) {
        return MOCK_PROJECTS;
    }
  });

  const [initialPrompt, setInitialPrompt] = useState<string>('');
  const [initialAspectRatio, setInitialAspectRatio] = useState<AspectRatio>('1:1');

  // Persist results to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('lola_assets', JSON.stringify(results));
    } catch (e) {
      console.error("Failed to save assets to storage", e);
    }
  }, [results]);

  // Persist projects
  useEffect(() => {
    try {
        localStorage.setItem('lola_projects', JSON.stringify(projects));
    } catch (e) {
        console.error("Failed to save projects", e);
    }
  }, [projects]);

  const handleCreateProject = (name: string, color: string) => {
    const newProject: Project = {
        id: Date.now().toString(),
        name,
        assetCount: 0,
        lastEdited: Date.now(),
        color
    };
    setProjects([newProject, ...projects]);
  };

  const handleSelectProject = (projectId: string) => {
    setActiveProjectId(projectId);
    setCurrentView(ViewState.RESULTS);
  };

  const handleNavigation = (view: ViewState) => {
    // If going to Home, clear the project context so new creations are "Global" by default
    // unless the user specifically wants to stay in the project. 
    // For this UX, going home usually resets context.
    if (view === ViewState.HOME) {
      setActiveProjectId(null);
    }
    setCurrentView(view);
  };

  // Handle starting a campaign from Home (URL or Template)
  const handleStartCampaign = (startData?: string) => {
    if (startData) {
      setInitialPrompt(startData);
    } else {
      setInitialPrompt('A futuristic sneaker on a neon city street'); // Default if empty
    }
    setInitialAspectRatio('1:1'); // Default
    setCurrentView(ViewState.PIPELINE);
  };

  // Handle Remixing an existing asset
  const handleRemix = (asset: GeneratedAsset) => {
    setInitialPrompt(asset.prompt);
    setInitialAspectRatio(asset.aspectRatio);
    setCurrentView(ViewState.PIPELINE);
  };

  // Handle transitioning from Pipeline to Results with new data
  const handleGenerationComplete = (imageUrls: string[], prompt: string, aspectRatio: AspectRatio) => {
    const newAssets: GeneratedAsset[] = imageUrls.map((url, idx) => ({
      id: Date.now().toString() + idx,
      url: url,
      type: 'image',
      aspectRatio: aspectRatio,
      createdAt: Date.now(),
      prompt: prompt,
      status: 'completed',
      projectId: activeProjectId || undefined // Assign to active project if one exists
    }));
    
    // Add new assets to the beginning of the list
    setResults([...newAssets, ...results]);
    
    // Update project asset count if relevant
    if (activeProjectId) {
        setProjects(prev => prev.map(p => 
            p.id === activeProjectId 
                ? { ...p, assetCount: p.assetCount + newAssets.length, lastEdited: Date.now() }
                : p
        ));
    }

    setCurrentView(ViewState.RESULTS);
  };

  // Handle deleting an asset
  const handleDeleteAsset = (id: string) => {
    setResults(prevResults => prevResults.filter(asset => asset.id !== id));
  };

  // Filter assets based on active project
  const displayedAssets = activeProjectId 
    ? results.filter(asset => asset.projectId === activeProjectId)
    : results;

  const activeProjectName = activeProjectId 
    ? projects.find(p => p.id === activeProjectId)?.name 
    : undefined;

  return (
    <div className="relative flex h-screen w-full max-w-md mx-auto flex-col overflow-hidden bg-background-light dark:bg-background-dark shadow-2xl">
      {/* Background Glow Effects (Global) */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[40%] bg-primary/20 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="absolute bottom-[10%] right-[-10%] w-[60%] h-[40%] bg-primary/10 rounded-full blur-[100px] pointer-events-none z-0"></div>

      {/* View Rendering */}
      <div className="flex-1 flex flex-col h-full z-10 overflow-hidden">
        {currentView === ViewState.HOME && (
          <Home 
            onNavigate={handleNavigation} 
            onStartCampaign={handleStartCampaign}
            recentAssets={results} // Home always shows latest globally
          />
        )}
        
        {currentView === ViewState.PROJECTS && (
          <Projects 
            onNavigate={handleNavigation} 
            projects={projects}
            onCreateProject={handleCreateProject}
            onSelectProject={handleSelectProject}
          />
        )}

        {currentView === ViewState.PIPELINE && (
          <Pipeline 
            initialPrompt={initialPrompt}
            initialAspectRatio={initialAspectRatio}
            onBack={() => handleNavigation(ViewState.HOME)} 
            onGenerationComplete={handleGenerationComplete} 
          />
        )}
        
        {currentView === ViewState.RESULTS && (
          <Results 
            assets={displayedAssets} 
            projectName={activeProjectName}
            onBack={() => handleNavigation(ViewState.HOME)}
            onClearProject={() => setActiveProjectId(null)} 
            onDeleteAsset={handleDeleteAsset}
            onRemix={handleRemix}
          />
        )}

        {currentView === ViewState.TEAM && (
          <Team />
        )}

        {currentView === ViewState.SETTINGS && (
          <Settings />
        )}
      </div>

      {/* Global Bottom Navigation - Only show on top-level views */}
      {(currentView === ViewState.HOME || currentView === ViewState.PROJECTS || currentView === ViewState.TEAM || currentView === ViewState.SETTINGS) && (
        <BottomNav currentView={currentView} onChangeView={handleNavigation} />
      )}
    </div>
  );
}