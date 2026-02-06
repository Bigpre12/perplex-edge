/**
 * LandingPage - Marketing home page with hero, features, and CTAs.
 * 
 * Drives users to /today (main dashboard) and /pricing.
 */

import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Top nav */}
      <header className="border-b border-gray-800">
        <div className="flex items-center justify-between max-w-6xl px-4 py-3 mx-auto">
          <Link to="/" className="text-lg font-bold flex items-center gap-2">
            <span className="text-blue-400">⚡</span> Perplex Edge
          </Link>
          <nav className="hidden sm:flex items-center gap-4 text-sm">
            <Link to="/today" className="hover:text-emerald-300">
              Today&apos;s Board
            </Link>
            <Link to="/props" className="hover:text-emerald-300">
              Props
            </Link>
            <Link to="/stats" className="hover:text-emerald-300">
              Stats
            </Link>
            <Link to="/parlay" className="hover:text-emerald-300">
              Parlay Builder
            </Link>
            <Link to="/pricing" className="hover:text-emerald-300">
              Pricing
            </Link>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl px-4 py-10 mx-auto">
        {/* Hero */}
        <section className="grid items-center gap-8 mb-12 md:grid-cols-2">
          <div>
            <h1 className="mb-4 text-3xl font-bold md:text-5xl leading-tight">
              Multi-sport player prop engine built for serious bettors.
            </h1>
            <p className="mb-6 text-base text-gray-300">
              One dashboard for EV, hit-rates, parlay building, and full slates across NBA, NFL, MLB, NHL, NCAAB, NCAAF, tennis, soccer, golf, UFC and more.
            </p>
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <Link
                to="/today"
                className="px-6 py-3 font-semibold text-gray-950 bg-emerald-400 rounded-lg hover:bg-emerald-300 transition-colors"
              >
                See today&apos;s board
              </Link>
              <Link
                to="/pricing"
                className="px-6 py-3 border border-gray-600 rounded-lg hover:border-emerald-300 transition-colors"
              >
                View pricing
              </Link>
              <span className="text-gray-400">
                No picks sold. Just edges and tools.
              </span>
            </div>
          </div>

          {/* Simple product preview blocks */}
          <div className="grid gap-3 text-sm">
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800 animate-fade-in">
              <div className="mb-1 text-xs font-semibold text-emerald-300">
                Player Props
              </div>
              <p className="text-sm text-gray-300">
                Ranked EV board with model win% and Kelly sizing across 16 sports, plus multi-book line shopping.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800 animate-fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="mb-1 text-xs font-semibold text-sky-300">
                Stats &amp; Trends
              </div>
              <p className="text-sm text-gray-300">
                Hot/Cold players, streaks, and market-level hit rates so you know exactly which props each player is crushing.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="mb-1 text-xs font-semibold text-amber-300">
                Smart Parlay Builder
              </div>
              <p className="text-sm text-gray-300">
                AI-optimized entries for DFS pick'em and sportsbooks with correlation checks and leg grades.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800 animate-fade-in" style={{ animationDelay: '0.3s' }}>
              <div className="mb-1 text-xs font-semibold text-purple-300">
                AI Edge
              </div>
              <p className="text-sm text-gray-300">
                AI-assisted prop analysis that surfaces hidden edges, ranks by confidence, and explains the reasoning.
              </p>
            </div>
          </div>
        </section>

        {/* Features */}
        {/* Stats Ticker */}
        <section className="mb-10 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 rounded-lg bg-gray-900/50 border border-gray-800">
            <div className="text-2xl font-bold text-emerald-400">16</div>
            <div className="text-xs text-gray-400 mt-1">Sports Covered</div>
          </div>
          <div className="p-4 rounded-lg bg-gray-900/50 border border-gray-800">
            <div className="text-2xl font-bold text-sky-400">500+</div>
            <div className="text-xs text-gray-400 mt-1">Daily Props</div>
          </div>
          <div className="p-4 rounded-lg bg-gray-900/50 border border-gray-800">
            <div className="text-2xl font-bold text-amber-400">10</div>
            <div className="text-xs text-gray-400 mt-1">Sportsbooks</div>
          </div>
          <div className="p-4 rounded-lg bg-gray-900/50 border border-gray-800">
            <div className="text-2xl font-bold text-purple-400">24/7</div>
            <div className="text-xs text-gray-400 mt-1">Auto-Refresh</div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="mb-4 text-lg font-bold">What you get</h2>
          <div className="grid gap-4 text-sm md:grid-cols-3">
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800">
              <h3 className="mb-1 font-semibold">Full multi-sport coverage</h3>
              <p className="text-sm text-gray-300">
                16 sports wired end-to-end: schedules, props, stats, and slates from NBA and NFL to EPL, UCL, PGA, UFC and tennis.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800">
              <h3 className="mb-1 font-semibold">Model-driven edges</h3>
              <p className="text-sm text-gray-300">
                EV, model win probability, hit-rate windows, and Kelly risk levels on every prop, plus 100%-hit trend panels.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-gray-900/70 border border-gray-800">
              <h3 className="mb-1 font-semibold">Your daily workflow</h3>
              <p className="text-sm text-gray-300">
                One Today page to scan top EV, check hot players, review streaks, and see tomorrow&apos;s slate in minutes.
              </p>
            </div>
          </div>
        </section>

        {/* Sports Supported */}
        <section className="mb-10 py-6 border-y border-gray-800">
          <h2 className="mb-4 text-lg font-bold text-center">Sports Covered</h2>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              'NBA', 'NFL', 'MLB', 'NHL', 'NCAAB', 'NCAAF', 'WNBA',
              'ATP', 'WTA', 'EPL', 'UCL', 'UEL', 'UECL', 'MLS', 'PGA', 'UFC'
            ].map((sport) => (
              <span
                key={sport}
                className="px-3 py-1.5 text-sm bg-gray-800 rounded-lg text-gray-300"
              >
                {sport}
              </span>
            ))}
          </div>
        </section>

        {/* CTA + social proof placeholder */}
        <section className="flex flex-col items-start gap-4 mb-8 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="mb-1 text-lg font-bold">Ready to plug this into your process?</h2>
            <p className="text-sm text-gray-300">
              Start on the free tier with NBA and NFL, upgrade to Pro when you&apos;re ready to go fully multi-sport.
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              to="/today"
              className="px-6 py-3 font-semibold text-gray-950 bg-emerald-400 rounded-lg hover:bg-emerald-300 transition-colors"
            >
              Open Today&apos;s Board
            </Link>
            <Link
              to="/pricing"
              className="px-6 py-3 border border-gray-600 rounded-lg hover:border-emerald-300 transition-colors"
            >
              See plans
            </Link>
          </div>
        </section>

        {/* Simple FAQ stub */}
        <section className="pb-10 border-t border-gray-800 pt-7">
          <h2 className="mb-4 text-lg font-bold">FAQ</h2>
          <div className="space-y-4 text-sm text-gray-300">
            <div>
              <p className="font-semibold text-gray-100">
                Do you sell picks?
              </p>
              <p>
                No. This is a research and analytics tool. You get model outputs, edges, and tools to build your own tickets.
              </p>
            </div>
            <div>
              <p className="font-semibold text-gray-100">
                Which books do you support?
              </p>
              <p>
                Major U.S. books and relevant alt-lines where available; the engine focuses on edges and line movement, not just one book.
              </p>
            </div>
            <div>
              <p className="font-semibold text-gray-100">
                What sports are included on Pro?
              </p>
              <p>
                All 16 mapped sports: NBA, NFL, NCAAB, NCAAF, WNBA, MLB, NHL, ATP, WTA, EPL, UCL, UEL, UECL, MLS, PGA, UFC.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-6">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500">
            <p>Smart Parlay Builder by Perplex Edge</p>
            <div className="flex gap-6">
              <Link to="/today" className="hover:text-white transition-colors">Today</Link>
              <Link to="/props" className="hover:text-white transition-colors">Props</Link>
              <Link to="/stats" className="hover:text-white transition-colors">Stats</Link>
              <Link to="/parlay" className="hover:text-white transition-colors">Parlay</Link>
              <Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
