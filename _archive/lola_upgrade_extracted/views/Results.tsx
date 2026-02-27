import React, { useState } from 'react';
import { GeneratedAsset, AspectRatio } from '../types';
import JSZip from 'jszip';
import FileSaver from 'file-saver';

interface ResultsProps {
  assets: GeneratedAsset[];
  projectName?: string;
  onBack: () => void;
  onClearProject: () => void;
  onDeleteAsset: (id: string) => void;
  onRemix: (asset: GeneratedAsset) => void;
}

export const Results: React.FC<ResultsProps> = ({ assets, projectName, onBack, onClearProject, onDeleteAsset, onRemix }) => {
  const [activeFilter, setActiveFilter] = useState<'ALL' | AspectRatio>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const filteredAssets = assets.filter(asset => {
    const matchesRatio = activeFilter === 'ALL' || asset.aspectRatio === activeFilter;
    const matchesSearch = searchQuery.trim() === '' || asset.prompt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRatio && matchesSearch;
  });

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleOpenLink = (url: string) => {
    window.open(url, '_blank');
  };

  const handleShare = () => {
    const shareUrl = window.location.href;
    navigator.clipboard.writeText(shareUrl).then(() => {
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    }).catch(err => {
      console.error('Failed to copy link', err);
    });
  };

  const handleExportAll = async () => {
    if (filteredAssets.length === 0) return;
    
    setIsExporting(true);
    const zip = new JSZip();
    const folder = zip.folder(projectName ? `${projectName.replace(/\s+/g, '-').toLowerCase()}-assets` : "lola-assets");
    
    if (folder) {
        let count = 0;
        const promises = filteredAssets.map(async (asset, index) => {
            try {
                const response = await fetch(asset.url);
                const blob = await response.blob();
                const ext = blob.type.split('/')[1] || 'png';
                folder.file(`asset-${index + 1}-${asset.aspectRatio.replace(':','-')}.${ext}`, blob);
                count++;
            } catch (e) {
                console.error("Failed to add file to zip", e);
            }
        });

        await Promise.all(promises);

        if (count > 0) {
            const content = await zip.generateAsync({ type: "blob" });
            FileSaver.saveAs(content, projectName ? `${projectName}-export.zip` : "lola-campaign-export.zip");
        }
    }
    setIsExporting(false);
  };

  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-white font-display overflow-x-hidden min-h-screen flex flex-col relative transition-colors duration-300">
      
      {/* Toast Notification */}
      <div className={`fixed top-24 left-1/2 -translate-x-1/2 z-[60] transition-all duration-300 transform ${showToast ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0 pointer-events-none'}`}>
        <div className="bg-surface-darker border border-white/10 text-white px-4 py-2 rounded-full shadow-xl flex items-center gap-2">
          <span className="material-symbols-outlined text-green-500 text-sm">check_circle</span>
          <span className="text-sm font-medium">Link copied to clipboard</span>
        </div>
      </div>

      {/* Sticky Header */}
      <header className="sticky top-0 z-50 bg-white/90 dark:bg-background-dark/95 backdrop-blur-md border-b border-slate-200 dark:border-white/5 pt-12 pb-2 px-4 transition-colors duration-300">
        <div className="flex items-center justify-between">
          <button onClick={onBack} className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-slate-100 dark:hover:bg-white/10 text-slate-900 dark:text-white transition-colors">
            <span className="material-symbols-outlined">arrow_back</span>
          </button>
          <div className="flex flex-col items-center">
            <h1 className="text-slate-900 dark:text-white text-lg font-bold leading-tight tracking-tight flex items-center gap-2">
                {projectName ? (
                    <>
                        <span className="max-w-[150px] truncate">{projectName}</span>
                        <span 
                            onClick={onClearProject}
                            className="material-symbols-outlined text-sm bg-slate-100 dark:bg-white/10 rounded-full p-0.5 cursor-pointer hover:bg-slate-200 dark:hover:bg-white/20"
                            title="Clear Filter"
                        >close</span>
                    </>
                ) : 'All Results'}
            </h1>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(182,19,236,0.8)]"></span>
              <span className="text-xs font-medium text-slate-500 dark:text-white/60 tracking-wide uppercase">
                {filteredAssets.length} Assets
              </span>
            </div>
          </div>
          <button className="flex items-center justify-center w-10 h-10 rounded-full hover:bg-slate-100 dark:hover:bg-white/10 text-primary transition-colors">
            <span className="material-symbols-outlined">edit</span>
          </button>
        </div>
      </header>

      {/* Search Bar */}
      <div className="px-4 mt-4">
        <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/50 to-pink-600/50 rounded-xl opacity-0 group-focus-within:opacity-100 transition duration-500 blur-sm"></div>
            <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-slate-400 dark:text-white/40">search</span>
                <input 
                    type="text" 
                    placeholder="Search by prompt..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-xl py-3 pl-10 pr-10 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 focus:outline-none focus:ring-0"
                />
                {searchQuery && (
                    <button 
                        onClick={() => setSearchQuery('')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:text-white/40 dark:hover:text-white"
                    >
                        <span className="material-symbols-outlined text-lg">cancel</span>
                    </button>
                )}
            </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="px-4 py-4">
        <div className="flex gap-3">
          <div className="flex-1 bg-white dark:bg-surface-dark rounded-xl p-4 border border-slate-200 dark:border-white/5 shadow-sm dark:shadow-none">
            <div className="flex items-start justify-between mb-2">
              <span className="p-1.5 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary">
                <span className="material-symbols-outlined text-[20px]">layers</span>
              </span>
            </div>
            <p className="text-slate-500 dark:text-white/60 text-xs font-medium uppercase tracking-wider">Variants</p>
            <p className="text-slate-900 dark:text-white text-2xl font-bold">{filteredAssets.length}</p>
          </div>
          <div className="flex-1 bg-white dark:bg-surface-dark rounded-xl p-4 border border-slate-200 dark:border-white/5 shadow-sm dark:shadow-none">
            <div className="flex items-start justify-between mb-2">
              <span className="p-1.5 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary">
                <span className="material-symbols-outlined text-[20px]">timer</span>
              </span>
            </div>
            <p className="text-slate-500 dark:text-white/60 text-xs font-medium uppercase tracking-wider">Runtime</p>
            <p className="text-slate-900 dark:text-white text-2xl font-bold">4s</p>
          </div>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="px-4 pb-4">
        <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2">
          <button 
            onClick={() => setActiveFilter('ALL')}
            className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors border ${activeFilter === 'ALL' ? 'bg-primary text-white border-primary/50 shadow-lg shadow-primary/20' : 'bg-white dark:bg-surface-dark border-slate-200 dark:border-white/10 text-slate-600 dark:text-white/70 hover:bg-slate-50 dark:hover:bg-white/5'}`}
          >
            All Assets
          </button>
          <button 
            onClick={() => setActiveFilter('9:16')}
            className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors border ${activeFilter === '9:16' ? 'bg-primary text-white border-primary/50 shadow-lg shadow-primary/20' : 'bg-white dark:bg-surface-dark border-slate-200 dark:border-white/10 text-slate-600 dark:text-white/70 hover:bg-slate-50 dark:hover:bg-white/5'}`}
          >
            Stories (9:16)
          </button>
          <button 
            onClick={() => setActiveFilter('4:5')}
            className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors border ${activeFilter === '4:5' ? 'bg-primary text-white border-primary/50 shadow-lg shadow-primary/20' : 'bg-white dark:bg-surface-dark border-slate-200 dark:border-white/10 text-slate-600 dark:text-white/70 hover:bg-slate-50 dark:hover:bg-white/5'}`}
          >
            Feed (4:5)
          </button>
          <button 
            onClick={() => setActiveFilter('1:1')}
            className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium transition-colors border ${activeFilter === '1:1' ? 'bg-primary text-white border-primary/50 shadow-lg shadow-primary/20' : 'bg-white dark:bg-surface-dark border-slate-200 dark:border-white/10 text-slate-600 dark:text-white/70 hover:bg-slate-50 dark:hover:bg-white/5'}`}
          >
            Square (1:1)
          </button>
        </div>
      </div>

      {/* Masonry Grid Gallery */}
      <div className="px-4 pb-32 columns-2 gap-4 space-y-4">
        {filteredAssets.map((asset) => (
          <div key={asset.id} className="relative break-inside-avoid rounded-xl overflow-hidden group bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/5 shadow-sm dark:shadow-none">
            <div className={`relative w-full ${asset.aspectRatio === '9:16' ? 'aspect-[9/16]' : asset.aspectRatio === '16:9' ? 'aspect-video' : 'aspect-square'}`}>
              <img src={asset.url} alt={asset.prompt} className="w-full h-full object-cover" />
              {/* Top Badge */}
              <div className="absolute top-2 left-2 px-2 py-1 glass-panel rounded-md">
                <span className="text-[10px] font-bold text-white tracking-widest uppercase">{asset.aspectRatio}</span>
              </div>
            </div>
            {/* Bottom Action Bar */}
            <div className="absolute bottom-0 inset-x-0 glass-panel p-2 flex items-center justify-between opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
              <div className="flex gap-1">
                <button 
                  onClick={() => handleDownload(asset.url, `lola-asset-${asset.id}.png`)}
                  className="w-7 h-7 rounded-full bg-white/10 hover:bg-primary hover:text-white text-white/80 flex items-center justify-center transition-all"
                  title="Download"
                >
                  <span className="material-symbols-outlined text-[16px]">download</span>
                </button>
                <button 
                  onClick={() => handleOpenLink(asset.url)}
                  className="w-7 h-7 rounded-full bg-white/10 hover:bg-white hover:text-surface-dark text-white/80 flex items-center justify-center transition-all"
                  title="Open Link"
                >
                  <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                </button>
                <button 
                  onClick={() => onDeleteAsset(asset.id)}
                  className="w-7 h-7 rounded-full bg-white/10 hover:bg-red-500/80 text-white/80 flex items-center justify-center transition-all"
                  title="Delete"
                >
                  <span className="material-symbols-outlined text-[16px]">delete</span>
                </button>
              </div>
              <button 
                onClick={() => onRemix(asset)}
                className="w-7 h-7 rounded-full bg-primary/20 text-primary hover:bg-primary hover:text-white flex items-center justify-center transition-all"
                title="Remix"
              >
                <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
              </button>
            </div>
          </div>
        ))}
        {/* Placeholder if empty */}
        {filteredAssets.length === 0 && (
          <div className="col-span-2 text-center py-10">
            <span className="material-symbols-outlined text-slate-300 dark:text-white/20 text-4xl mb-2">image_not_supported</span>
            <p className="text-slate-400 dark:text-white/40 text-sm">
                {searchQuery ? `No assets match "${searchQuery}"` : (projectName ? 'No assets in this project yet.' : 'No assets found.')}
            </p>
          </div>
        )}
      </div>

      {/* Fixed Bottom Actions Panel */}
      <div className="fixed bottom-0 left-0 right-0 p-4 z-40 bg-gradient-to-t from-background-light dark:from-background-dark via-background-light/90 dark:via-background-dark/90 to-transparent pt-12 transition-colors duration-300">
        <div className="flex gap-3 max-w-md mx-auto">
          <button 
            onClick={handleExportAll}
            disabled={filteredAssets.length === 0 || isExporting}
            className="flex-1 bg-gradient-to-r from-primary to-[#d946ef] text-white py-3.5 px-4 rounded-xl font-bold shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all active:scale-[0.98] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isExporting ? (
                <span className="size-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
                <span className="material-symbols-outlined text-[20px]">download</span>
            )}
            <span>{isExporting ? 'Zipping...' : 'Export All (ZIP)'}</span>
          </button>
          <button 
            onClick={handleShare}
            className="bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white py-3.5 px-4 rounded-xl font-bold hover:bg-slate-50 dark:hover:bg-white/5 transition-all active:scale-[0.98] flex items-center justify-center gap-2 backdrop-blur-md"
          >
            <span className="material-symbols-outlined text-[20px]">share</span>
          </button>
        </div>
      </div>
    </div>
  );
};