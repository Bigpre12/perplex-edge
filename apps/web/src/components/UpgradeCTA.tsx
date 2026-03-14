export default function UpgradeCTA({ feature, description }: { feature: string; description?: string }) {
  return (
    <div className="bg-black/30 border border-white/10 rounded-xl p-6 text-center shadow-lg">
      <div className="mx-auto w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mb-4">
        <span className="text-xl">🔒</span>
      </div>
      <h3 className="text-white font-bold text-lg mb-2 uppercase tracking-wide">
        Unlock {feature}
      </h3>
      {description && (
        <p className="text-slate-400 text-sm mb-4 px-4 font-medium leading-relaxed">
          {description}
        </p>
      )}
      <button className="bg-gradient-to-r from-[#F5C518] to-yellow-600 hover:from-yellow-400 hover:to-yellow-500 text-black px-6 py-2.5 rounded-full font-black uppercase tracking-widest text-xs transition-all shadow-md transform hover:scale-105 active:scale-95 text-shadow-sm">
        Upgrade to Premium
      </button>
    </div>
  );
}
