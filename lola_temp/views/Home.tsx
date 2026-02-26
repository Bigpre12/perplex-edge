import React, { useState } from 'react';
import { ViewState, GeneratedAsset } from '../types';

interface HomeProps {
  onNavigate: (view: ViewState) => void;
  onStartCampaign?: (initialData: string) => void;
  recentAssets: GeneratedAsset[];
}

const templates = [
  {
    id: 'product-gallery',
    title: 'Product Gallery',
    desc: 'Studio quality shots generated instantly.',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCR6madPuJD4Z9mhNpMMFkc96AjPJ1SyBE55WiiXa_IkRQMjJEQ7ck0dU6ywr6n8m1HmQplbXZFVIUlZH0FaKOjhf_RFeFdTzDszaCJxk9eJ1kSxo52koFVM2pz-xHGrhMIqLTA78mOhs6NjmXWPNXOLjIkwHbIS6aT9nZksdzQXAZkVTEvQ5iCekvca-NvthAx_4uHVDcF9vhZ4RRY1NsCLxCK71ATrGohh0kVZnubCA4i2S0Su9rNZ2JGhElVFCRXzzM2gezgTD8',
    icon: 'photo_camera',
    badge: { text: 'High Res', color: 'text-primary', border: 'border-primary/20', bg: 'bg-white/10' },
    defaultPrompt: 'Studio photography of a sleek modern product, professional lighting, 4k'
  },
  {
    id: 'social-pack',
    title: 'Social Ad Pack',
    desc: 'Insta & TikTok ready visuals.',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB4Fowbot6T8xI4sqKvwv1rkSgrdOj_y-QWLwaamAGewsQxKjIJdlovUHlGdMNILStnDO4N14QH4mFldmFOy5fjsOMfAxgbWtq5r-BqSmuRgmObK0UqtwnpbxOYrCaKB73knkAjhMpPj411FChqTXB9phUpzFpuyZU1FhSeL2CAgvHbIXjjlodWBKyL319D8s5JtpEAxH2TgzYQvUtXFFRDyRvmUKgWCpzI77Wb4JeGMzAKnHZFELocuaTvoz6KpoGWFBl_ISMjGWg',
    icon: 'campaign',
    badge: { text: '9:16', color: 'text-blue-400', border: 'border-blue-400/20', bg: 'bg-white/10' },
    defaultPrompt: 'Lifestyle social media shot, vibrant colors, influencer style, trending aesthetics'
  },
  {
    id: 'amazon-listing',
    title: 'Amazon Pack',
    desc: 'White background & lifestyle mix.',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBOdYBC_glQTjEqWCgxt7CROLFIf2i2QP_ZbrwT9uOoA7G34T7jcWKofn-c4MBvD_jDn9z4rwtAExlCLDmuwZRgUXfT_H2fLZN14NTpF3qOB9vqVzVrGHR9yGGY04Uj1XwPp-2OKkHkfAWXfmDvfAvWhMvo7QWPWLgEjFjysKvYBSUMmWcXBcWt8ioymzSNK9dOwv2LHmNLnmgpngAegeFdMOHvTcTAuxSwycXveMvnqTi-y7RsBDY0yySDYnFl-atYIcGrf0bLW1A',
    icon: 'shopping_cart',
    badge: { text: 'Mixed', color: 'text-orange-400', border: 'border-orange-400/20', bg: 'bg-white/10' },
    defaultPrompt: 'Product on pure white background, commercial e-commerce photography'
  }
];

export const Home: React.FC<HomeProps> = ({ onNavigate, onStartCampaign, recentAssets }) => {
  const [inputValue, setInputValue] = useState('');

  const handleAction = (data: string) => {
    if (onStartCampaign) {
      onStartCampaign(data);
    } else {
      onNavigate(ViewState.PIPELINE);
    }
  };

  const handleInputSubmit = () => {
    if (!inputValue.trim()) return;
    
    // Simulate simple scraping logic
    let prompt = inputValue;
    if (inputValue.includes('http') || inputValue.includes('www')) {
        prompt = `Commercial product photography of a product from ${inputValue}, studio lighting, high resolution`;
    }
    handleAction(prompt);
  };

  return (
    <div className="flex-1 overflow-y-auto overflow-x-hidden no-scrollbar pb-24 z-10 px-4">
      {/* Header */}
      <div className="flex items-center justify-between pt-8 pb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div 
              className="bg-center bg-no-repeat bg-cover rounded-full size-10 ring-2 ring-primary/30"
              style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAmHP9GAX8n2ixx76jka6Xa40HnbCE9b7hb6n-6LkS5muPV3wbNNxO_NBbpW_tNONs0E7JsI1XqvFtBQhCM4xfnvAglOkOn3AVkuO2SH4ioTSO6YUft4AkI5L1VTz1CrfTST1hnP81LNyyrWweUqTFW5NO9ODMHqMTY5yF2j-X8mrhrHioSoEdiEuQLhKBS5tBBJfLrVuUT_zgOSen00wyP1dS7_pOyEfXW8fTySHm9s8Nvm2z9H02rAYPBAV3cU7ECx2Bc-wU765Q")' }}
            ></div>
            <div className="absolute bottom-0 right-0 size-3 bg-green-500 rounded-full border-2 border-background-light dark:border-background-dark"></div>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-white/60 font-medium tracking-wide uppercase">Creative Engine</p>
            <h2 className="text-slate-900 dark:text-white text-xl font-bold tracking-tight">LOLA</h2>
          </div>
        </div>
        <button className="relative flex items-center justify-center size-10 rounded-full bg-white dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors border border-slate-200 dark:border-white/5 group shadow-sm dark:shadow-none">
          <span className="material-symbols-outlined text-slate-600 dark:text-white/80 group-hover:text-primary dark:group-hover:text-white transition-colors" style={{ fontSize: '24px' }}>notifications</span>
          <span className="absolute top-2 right-2.5 size-2 bg-primary rounded-full animate-pulse"></span>
        </button>
      </div>

      {/* Hero */}
      <div className="mt-2 mb-6 px-2">
        <h1 className="text-slate-900 dark:text-white text-[32px] font-bold leading-[1.1] tracking-tight">
          What do you want <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-pink-600 dark:from-white dark:to-white/50">to create today?</span>
        </h1>
      </div>

      {/* URL Input (Wired Up) */}
      <div className="px-2 mb-8">
         <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-pink-600 rounded-xl opacity-30 group-hover:opacity-60 transition duration-500 blur"></div>
            <div className="relative flex items-center bg-white dark:bg-surface-dark border border-slate-200 dark:border-white/10 rounded-xl p-1.5 shadow-xl">
               <div className="flex items-center justify-center size-10 rounded-lg bg-slate-100 dark:bg-surface-darker text-slate-400 dark:text-white/40">
                  <span className="material-symbols-outlined">link</span>
               </div>
               <input 
                  type="text" 
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleInputSubmit()}
                  placeholder="Paste URL to auto-generate campaign..." 
                  className="flex-1 bg-transparent border-none text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/30 focus:ring-0 text-sm px-3"
               />
               <button 
                onClick={handleInputSubmit}
                className="size-10 bg-primary rounded-lg flex items-center justify-center text-white shadow-lg shadow-primary/20 hover:scale-105 transition-transform active:scale-95">
                  <span className="material-symbols-outlined">auto_awesome</span>
               </button>
            </div>
         </div>
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 gap-4 px-2 mb-8">
        {templates.map((template) => (
          <div 
            key={template.id}
            onClick={() => handleAction(template.defaultPrompt)}
            className="group relative overflow-hidden rounded-2xl glass-panel p-1 transition-all hover:scale-[1.01] active:scale-[0.99] cursor-pointer"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="flex items-stretch gap-4 bg-white/50 dark:bg-surface-dark/40 rounded-xl p-4 h-full relative z-10">
              <div className="w-24 h-24 shrink-0 rounded-lg overflow-hidden relative shadow-lg">
                <img src={template.img} alt={template.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end justify-center pb-2">
                  <span className="material-symbols-outlined text-white" style={{ fontSize: '20px' }}>{template.icon}</span>
                </div>
              </div>
              <div className="flex flex-col justify-center flex-1">
                <h3 className="text-slate-900 dark:text-white text-lg font-bold mb-1">{template.title}</h3>
                <p className="text-slate-500 dark:text-white/60 text-sm mb-3 line-clamp-2">{template.desc}</p>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${template.badge.bg} ${template.badge.color} border ${template.badge.border} tracking-wider`}>
                    {template.badge.text}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <button className="size-8 rounded-full bg-slate-200 dark:bg-white/10 flex items-center justify-center group-hover:bg-primary transition-all group-hover:shadow-[0_0_20px_rgba(182,19,236,0.6)]">
                  <span className="material-symbols-outlined text-slate-600 dark:text-white group-hover:text-white" style={{ fontSize: '20px' }}>arrow_forward</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Creations (Dynamic) */}
      <div className="px-2 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-slate-900 dark:text-white text-lg font-bold tracking-tight">Recent Creations</h2>
          <button 
            onClick={() => onNavigate(ViewState.RESULTS)} 
            className="text-primary text-xs font-medium hover:text-primary/80 transition-colors"
          >
            View Gallery
          </button>
        </div>
        
        {recentAssets.length === 0 ? (
           <div className="text-slate-400 dark:text-white/40 text-sm p-8 bg-white dark:bg-surface-dark rounded-xl border border-dashed border-slate-200 dark:border-white/10 text-center shadow-sm dark:shadow-none">
             <span className="material-symbols-outlined text-3xl mb-2 opacity-50">imagesmode</span>
             <p>No assets created yet.</p>
             <p className="text-xs mt-1">Start a campaign above!</p>
           </div>
        ) : (
            <div className="flex gap-4 overflow-x-auto no-scrollbar pb-4 snap-x snap-mandatory">
            {recentAssets.slice(0, 10).map((asset) => (
                <div 
                key={asset.id}
                onClick={() => onNavigate(ViewState.RESULTS)}
                className="relative w-[140px] shrink-0 snap-start group cursor-pointer"
                >
                <div className={`rounded-xl overflow-hidden relative shadow-lg bg-surface-dark border border-white/5 ${asset.aspectRatio === '9:16' ? 'aspect-[9/16]' : 'aspect-square'}`}>
                    <img 
                    src={asset.url} 
                    alt={asset.prompt} 
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" 
                    loading="lazy"
                    />
                    <div className="absolute top-2 right-2">
                    <div className="bg-black/60 backdrop-blur-md rounded-full px-2 py-0.5 border border-white/10 flex items-center gap-1">
                        <div className="size-1.5 rounded-full bg-green-500"></div>
                        <span className="text-[9px] font-bold text-white uppercase">DONE</span>
                    </div>
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent opacity-80"></div>
                    <div className="absolute bottom-3 left-3 right-3">
                    <p className="text-white text-xs font-bold truncate">{asset.prompt}</p>
                    <p className="text-white/50 text-[10px]">{new Date(asset.createdAt).toLocaleDateString()}</p>
                    </div>
                </div>
                </div>
            ))}
            </div>
        )}
      </div>
      
      {/* Spacer for Bottom Nav */}
      <div className="h-8"></div>
    </div>
  );
};