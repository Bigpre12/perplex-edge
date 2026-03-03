import React, { useState } from 'react';
import { AspectRatio, NodeData } from '../types';
import { generateImageWithGemini } from '../services/geminiService';

interface PipelineProps {
  initialPrompt?: string;
  initialAspectRatio?: AspectRatio;
  onBack: () => void;
  onGenerationComplete: (imageUrls: string[], prompt: string, aspectRatio: AspectRatio) => void;
}

const STYLES = [
  { id: 'realistic', label: 'Studio Realistic', icon: 'photo_camera', prompt: 'photorealistic, 8k, highly detailed, studio lighting, professional photography' },
  { id: 'neon', label: 'Neon Cyberpunk', icon: 'bolt', prompt: 'cyberpunk, neon lighting, futuristic, glowing, vibrant colors, night time' },
  { id: 'minimal', label: 'Minimalist', icon: 'check_circle', prompt: 'minimalist, clean background, soft lighting, pastel colors, simple' },
  { id: 'cinematic', label: 'Cinematic', icon: 'movie', prompt: 'cinematic lighting, dramatic atmosphere, movie scene, color graded, anamorphic lens' },
  { id: '3d', label: '3D Render', icon: 'view_in_ar', prompt: '3d render, unreal engine 5, octane render, clay material, isometric' }
];

export const Pipeline: React.FC<PipelineProps> = ({ initialPrompt, initialAspectRatio, onBack, onGenerationComplete }) => {
  // State
  const [prompt, setPrompt] = useState(initialPrompt || 'A futuristic sneaker on a neon city street');
  const [styleId, setStyleId] = useState('realistic');
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>(initialAspectRatio || '1:1');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>('node-input'); 
  const [showSaveToast, setShowSaveToast] = useState(false);
  
  // Dynamic Nodes
  const nodes: NodeData[] = [
    { id: 'node-input', type: 'input', label: 'Input', icon: 'input', x: 50, y: 40 },
    { id: 'node-style', type: 'model', label: 'Style', icon: 'palette', x: 50, y: 190 }, // Using 'model' type for visual consistency for now
    { id: 'node-model', type: 'model', label: 'Gemini 2.5', icon: 'psychology', x: 50, y: 340 },
    { id: 'node-output', type: 'output', label: 'Result', icon: 'image', x: 50, y: 490 }
  ];

  const handleRunPipeline = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setError(null);
    setSelectedNode('node-output');
    
    try {
      // Construct the final prompt with style modifiers
      const selectedStyle = STYLES.find(s => s.id === styleId);
      const finalPrompt = selectedStyle 
        ? `${prompt}, ${selectedStyle.prompt}` 
        : prompt;

      console.log("Generating with prompt:", finalPrompt);

      const imageUrl = await generateImageWithGemini(finalPrompt, aspectRatio);
      onGenerationComplete([imageUrl], finalPrompt, aspectRatio);
    } catch (err) {
      setError("Failed to generate assets. Please try again.");
      console.error(err);
      setIsGenerating(false);
    }
  };

  const handleSave = () => {
    setShowSaveToast(true);
    setTimeout(() => setShowSaveToast(false), 2000);
  };

  const getConnectorPath = (start: {x: number, y: number}, end: {x: number, y: number}) => {
    // Calculate relative coordinates in the SVG space
    const startX = '50%';
    const startY = start.y + 70; // Node height approx
    const endX = '50%';
    const endY = end.y - 10;
    
    return `M ${startX} ${startY} C ${startX} ${startY + 30}, ${endX} ${endY - 30}, ${endX} ${endY}`;
  };

  return (
    <div className="flex flex-col h-full bg-surface-darker relative overflow-hidden">
      
      {/* Toast */}
      <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-[60] transition-all duration-300 transform ${showSaveToast ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0 pointer-events-none'}`}>
        <div className="bg-surface-darker border border-white/10 text-white px-4 py-2 rounded-full shadow-xl flex items-center gap-2">
          <span className="material-symbols-outlined text-green-500 text-sm">check_circle</span>
          <span className="text-sm font-medium">Workflow saved!</span>
        </div>
      </div>

      {/* Header */}
      <header className="flex items-center justify-between p-4 bg-surface-darker/90 backdrop-blur-md z-50 border-b border-white/5">
        <button onClick={onBack} className="flex items-center justify-center size-10 rounded-full hover:bg-white/10 transition-colors">
          <span className="material-symbols-outlined text-white">arrow_back</span>
        </button>
        <div className="flex flex-col items-center">
          <h1 className="text-base font-bold tracking-wide text-white">Workflow Editor</h1>
          <span className="text-xs text-primary font-medium tracking-wider uppercase">Visual Pipeline</span>
        </div>
        <button 
            onClick={handleSave}
            className="flex items-center justify-center size-10 rounded-full hover:bg-white/10 transition-colors"
        >
          <span className="material-symbols-outlined text-primary">save</span>
        </button>
      </header>

      {/* Canvas Area */}
      <main className="relative flex-1 w-full overflow-hidden bg-surface-darker">
        {/* Grid Background */}
        <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none"></div>

        {/* SVG Connections Layer */}
        <div className="absolute inset-0 pointer-events-none z-0">
          <svg className="w-full h-full overflow-visible">
             <defs>
               <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                 <stop offset="0%" stopColor="#b613ec" stopOpacity="0.2" />
                 <stop offset="100%" stopColor="#b613ec" stopOpacity="0.8" />
               </linearGradient>
             </defs>
             {/* Path 1: Input -> Style */}
             <path d={getConnectorPath(nodes[0], nodes[1])} stroke="url(#lineGradient)" strokeWidth="2" fill="none" className="text-primary" />
             {/* Path 2: Style -> Model */}
             <path d={getConnectorPath(nodes[1], nodes[2])} stroke="url(#lineGradient)" strokeWidth="2" fill="none" className="text-primary" />
             {/* Path 3: Model -> Output */}
             <path 
               d={getConnectorPath(nodes[2], nodes[3])} 
               stroke={isGenerating ? "#b613ec" : "#ffffff30"} 
               strokeWidth="2" 
               strokeDasharray="6 4" 
               fill="none" 
               className={`transition-all duration-500 ${isGenerating ? 'animate-dash opacity-100' : 'opacity-50'}`} 
             />
          </svg>
        </div>

        {/* Nodes Container */}
        <div className="absolute inset-0 flex flex-col items-center pt-6 px-4 overflow-y-auto no-scrollbar pb-40">
          
          {/* Node 1: Input */}
          <div 
            onClick={() => setSelectedNode('node-input')}
            className={`relative z-10 w-full max-w-sm bg-surface-dark border transition-all duration-300 rounded-xl shadow-lg flex flex-col mb-8 cursor-pointer
              ${selectedNode === 'node-input' ? 'border-primary shadow-[0_0_15px_rgba(182,19,236,0.3)] ring-1 ring-primary/50' : 'border-white/10 hover:border-white/30'}`}
          >
            <div className="flex items-center justify-between p-3 border-b border-white/5 bg-white/5 rounded-t-xl">
              <div className="flex items-center gap-2">
                <span className={`material-symbols-outlined text-[20px] ${selectedNode === 'node-input' ? 'text-primary' : 'text-white/60'}`}>input</span>
                <span className="text-sm font-bold text-white">Input Prompt</span>
              </div>
              <div className={`size-2 rounded-full ${prompt.length > 5 ? 'bg-green-500' : 'bg-red-500'}`}></div>
            </div>
            <div className="p-3">
              <p className="text-xs text-white/60 line-clamp-2 italic">"{prompt}"</p>
            </div>
            <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-primary rounded-full border-2 border-surface-dark"></div>
          </div>

          {/* Node 2: Style (New) */}
          <div 
            onClick={() => setSelectedNode('node-style')}
            className={`relative z-10 w-full max-w-sm bg-surface-dark border transition-all duration-300 rounded-xl shadow-lg flex flex-col mb-8 cursor-pointer
              ${selectedNode === 'node-style' ? 'border-primary shadow-[0_0_15px_rgba(182,19,236,0.3)] ring-1 ring-primary/50' : 'border-white/10 hover:border-white/30'}`}
          >
            <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-surface-dark border-2 border-primary rounded-full"></div>
            <div className="flex items-center justify-between p-3 border-b border-white/5 bg-white/5 rounded-t-xl">
              <div className="flex items-center gap-2">
                <span className={`material-symbols-outlined text-[20px] ${selectedNode === 'node-style' ? 'text-primary' : 'text-white/60'}`}>palette</span>
                <span className="text-sm font-bold text-white">Visual Style</span>
              </div>
            </div>
            <div className="p-3 flex items-center gap-3">
               <div className="size-8 rounded bg-primary/20 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-lg">{STYLES.find(s => s.id === styleId)?.icon || 'style'}</span>
               </div>
               <div>
                  <div className="text-sm font-bold text-white">{STYLES.find(s => s.id === styleId)?.label}</div>
                  <div className="text-[10px] text-white/40 uppercase tracking-wider">Preset</div>
               </div>
            </div>
            <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-primary rounded-full border-2 border-surface-dark"></div>
          </div>

          {/* Node 3: Model */}
          <div 
             onClick={() => setSelectedNode('node-model')}
             className={`relative z-10 w-full max-w-sm bg-surface-dark border transition-all duration-300 rounded-xl shadow-lg flex flex-col mb-8 cursor-pointer
              ${selectedNode === 'node-model' ? 'border-primary shadow-[0_0_15px_rgba(182,19,236,0.3)] ring-1 ring-primary/50' : 'border-white/10 hover:border-white/30'}`}
          >
             <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-surface-dark border-2 border-primary rounded-full"></div>
             <div className="flex items-center justify-between p-3 border-b border-white/5 bg-white/5 rounded-t-xl">
               <div className="flex items-center gap-2">
                 <span className={`material-symbols-outlined text-[20px] ${selectedNode === 'node-model' ? 'text-primary' : 'text-white/60'}`}>psychology</span>
                 <span className="text-sm font-bold text-white">Gemini 2.5</span>
               </div>
               <span className="text-[10px] bg-primary/20 text-primary px-1.5 py-0.5 rounded border border-primary/20">IMAGE</span>
             </div>
             <div className="p-3 grid grid-cols-2 gap-2">
                 <div className="bg-surface-darker p-2 rounded border border-white/5">
                   <div className="text-[10px] text-white/50 uppercase">Ratio</div>
                   <div className="text-sm font-bold text-white">{aspectRatio}</div>
                 </div>
                 <div className="bg-surface-darker p-2 rounded border border-white/5">
                   <div className="text-[10px] text-white/50 uppercase">Guidance</div>
                   <div className="text-sm font-bold text-white">Balanced</div>
                 </div>
             </div>
             <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-primary rounded-full border-2 border-surface-dark"></div>
          </div>

          {/* Node 4: Output */}
          <div 
             onClick={() => setSelectedNode('node-output')}
             className={`relative z-10 w-full max-w-sm bg-surface-dark border transition-all duration-300 rounded-xl shadow-lg flex flex-col cursor-pointer
              ${selectedNode === 'node-output' ? 'border-primary shadow-[0_0_15px_rgba(182,19,236,0.3)] ring-1 ring-primary/50' : 'border-white/10 hover:border-white/30'}
              ${isGenerating ? 'animate-pulse-fast border-primary/50' : ''}`}
          >
             <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-surface-dark border-2 border-white/40 rounded-full"></div>
             <div className="flex items-center justify-between p-3 border-b border-white/5 bg-white/5 rounded-t-xl">
               <div className="flex items-center gap-2">
                 <span className={`material-symbols-outlined text-[20px] ${isGenerating ? 'text-primary animate-spin' : 'text-white/60'}`}>output</span>
                 <span className="text-sm font-bold text-white">Result</span>
               </div>
             </div>
             <div className="p-3">
               <div className={`w-full rounded bg-surface-darker border-2 border-dashed border-white/10 flex flex-col items-center justify-center gap-2 overflow-hidden ${aspectRatio === '9:16' ? 'aspect-[9/16]' : aspectRatio === '16:9' ? 'aspect-video' : 'aspect-square'}`}>
                 {isGenerating ? (
                    <>
                       <div className="size-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
                       <span className="text-xs text-white/50 animate-pulse">Processing...</span>
                    </>
                 ) : (
                    <>
                       <span className="material-symbols-outlined text-white/20 text-4xl">image</span>
                       <span className="text-xs text-white/30">Ready</span>
                    </>
                 )}
               </div>
             </div>
          </div>

        </div>

        {/* Properties Overlay / Floating Panel */}
        <div className={`absolute bottom-20 inset-x-4 bg-glass-panel glass-panel rounded-xl p-4 transition-transform duration-300 z-40 ${selectedNode ? 'translate-y-0' : 'translate-y-[150%]'}`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
               <span className="material-symbols-outlined text-primary text-sm">tune</span>
               {selectedNode === 'node-input' && 'Edit Prompt'}
               {selectedNode === 'node-style' && 'Select Style'}
               {selectedNode === 'node-model' && 'Model Settings'}
               {selectedNode === 'node-output' && 'Output Preview'}
            </h3>
            <button onClick={(e) => { e.stopPropagation(); setSelectedNode(null); }} className="text-white/40 hover:text-white">
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>
          
          {selectedNode === 'node-input' && (
             <textarea 
               value={prompt} 
               onChange={(e) => setPrompt(e.target.value)}
               className="w-full h-24 bg-surface-darker border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-primary/50 resize-none"
               placeholder="Describe your image..."
             />
          )}

          {selectedNode === 'node-style' && (
             <div className="grid grid-cols-2 gap-2 max-h-[160px] overflow-y-auto no-scrollbar">
                {STYLES.map((style) => (
                  <button 
                    key={style.id}
                    onClick={() => setStyleId(style.id)}
                    className={`flex items-center gap-2 p-2 rounded-lg border transition-all ${styleId === style.id ? 'bg-primary/20 border-primary text-white' : 'bg-surface-darker border-white/10 text-white/60 hover:bg-white/5'}`}
                  >
                    <span className="material-symbols-outlined text-lg">{style.icon}</span>
                    <span className="text-xs font-bold">{style.label}</span>
                  </button>
                ))}
             </div>
          )}

          {selectedNode === 'node-model' && (
             <div className="space-y-4">
                <div>
                  <label className="text-xs text-white/50 uppercase font-bold mb-2 block">Aspect Ratio</label>
                  <div className="flex gap-2 flex-wrap">
                    {(['1:1', '9:16', '16:9', '4:3', '3:4'] as AspectRatio[]).map((r) => (
                      <button 
                        key={r}
                        onClick={() => setAspectRatio(r)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${aspectRatio === r ? 'bg-primary text-white border-primary' : 'bg-surface-darker text-white/60 border-white/10 hover:border-white/30'}`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>
             </div>
          )}

          {selectedNode === 'node-output' && (
             <div className="text-center py-4">
               <p className="text-white/60 text-sm">Run the pipeline to see results.</p>
             </div>
          )}
        </div>
      </main>

      {/* Bottom Action Bar */}
      <footer className="bg-surface-darker border-t border-white/5 p-4 safe-area-bottom z-50">
        <div className="flex items-center gap-4">
          <div className="flex flex-col flex-1">
             <span className="text-xs text-white/50 font-medium">Est. Time</span>
             <span className="text-sm font-bold text-white">~4s</span>
          </div>
          <button 
            onClick={handleRunPipeline}
            disabled={isGenerating || !prompt.trim()}
            className={`flex-[3] bg-gradient-to-r from-primary to-[#d946ef] text-white h-12 rounded-lg font-bold text-base flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(182,19,236,0.3)] transition-all ${isGenerating ? 'opacity-70 cursor-not-allowed' : 'hover:shadow-[0_0_25px_rgba(182,19,236,0.5)] active:scale-[0.98]'}`}
          >
            <span className="material-symbols-outlined">{isGenerating ? 'hourglass_empty' : 'play_arrow'}</span>
            {isGenerating ? 'Processing...' : 'Run Pipeline'}
          </button>
        </div>
        {error && <p className="text-red-500 text-xs text-center mt-2">{error}</p>}
      </footer>
    </div>
  );
};