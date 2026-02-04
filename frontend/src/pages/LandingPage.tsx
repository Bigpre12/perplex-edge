/**
 * LandingPage - Marketing home page with hero, features, and CTAs.
 * 
 * Drives users to /today (main dashboard) and /pricing.
 */

import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-gray-100">
      {/* Top nav */}
      <header className="border-b border-slate-800">
        <div className="flex items-center justify-between max-w-6xl px-4 py-3 mx-auto">
          <Link to="/" className="text-sm font-semibold">
            Perplex Engine
          </Link>
          <nav className="flex items-center gap-4 text-xs">
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
            <h1 className="mb-3 text-2xl font-semibold md:text-3xl">
              Multi-sport player prop engine built for serious bettors.
            </h1>
            <p className="mb-4 text-sm text-gray-300">
              One dashboard for EV, hit-rates, parlay building, and full slates across NBA, NFL, MLB, NHL, NCAAB, NCAAF, tennis, soccer, golf, UFC and more.
            </p>
            <div className="flex flex-wrap items-center gap-3 text-xs">
              <Link
                to="/today"
                className="px-4 py-2 font-semibold text-slate-950 bg-emerald-400 rounded hover:bg-emerald-300"
              >
                See today&apos;s board
              </Link>
              <Link
                to="/pricing"
                className="px-4 py-2 border border-slate-600 rounded hover:border-emerald-300"
              >
                View pricing
              </Link>
              <span className="text-gray-400">
                No picks sold. Just edges and tools.
              </span>
            </div>
          </div>

          {/* Simple product preview blocks */}
          <div className="grid gap-3 text-xs">
            <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
              <div className="mb-1 text-[11px] font-semibold text-emerald-300">
                Player Props
              </div>
              <p className="text-gray-300">
                Ranked EV board with model win% and Kelly sizing across 16 sports, plus multi-book line shopping.
              </p>
            </div>
            <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
              <div className="mb-1 text-[11px] font-semibold text-sky-300">
                Stats &amp; Trends
              </div>
              <p className="text-gray-300">
                Hot/Cold players, streaks, and market-level hit rates so you know exactly which props each player is crushing.
              </p>
            </div>
            <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
              <div className="mb-1 text-[11px] font-semibold text-amber-300">
                Parlay Builder
              </div>
              <p className="text-gray-300">
                Multi-sport and same-game parlays with correlation checks and leg grades, built directly from your prop board.
              </p>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="mb-10">
          <h2 className="mb-3 text-sm font-semibold">What you get</h2>
          <div className="grid gap-4 text-xs md:grid-cols-3">
            <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
              <h3 className="mb-1 font-semibold">Full multi-sport coverage</h3>
              <p className="text-gray-300">
                16 sports wired end-to-end: schedules, props, stats, and slates from NBA and NFL to EPL, UCL, PGA, UFC and tennis.
              </p>
            </div>
            <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
              <h3 className="mb-1 font-semibold">Model-driven edges</h3>
              <p className="text-gray-300">
                EV, model win probability, hit-rate windows, and Kelly risk levels on every prop, plus 100%-hit trend panels.
              </p>
            </div>
            <div className="p-3 rounded bg-slate-900/70 border border-slate-800">
              <h3 className="mb-1 font-semibold">Your daily workflow</h3>
              <p className="text-gray-300">
                One Today page to scan top EV, check hot players, review streaks, and see tomorrow&apos;s slate in minutes.
              </p>
            </div>
          </div>
        </section>

        {/* Sports Supported */}
        <section className="mb-10 py-6 border-y border-slate-800">
          <h2 className="mb-3 text-sm font-semibold text-center">Sports Covered</h2>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              'NBA', 'NFL', 'MLB', 'NHL', 'NCAAB', 'NCAAF', 'WNBA',
              'ATP', 'WTA', 'EPL', 'UCL', 'UEL', 'UECL', 'MLS', 'PGA', 'UFC'
            ].map((sport) => (
              <span
                key={sport}
                className="px-3 py-1 text-xs bg-slate-800 rounded text-gray-300"
              >
                {sport}
              </span>
            ))}
          </div>
        </section>

        {/* CTA + social proof placeholder */}
        <section className="flex flex-col items-start gap-3 mb-8 text-xs md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="mb-1 text-sm font-semibold">Ready to plug this into your process?</h2>
            <p className="text-gray-300">
              Start on the free tier with NBA and NFL, upgrade to Pro when you&apos;re ready to go fully multi-sport.
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              to="/today"
              className="px-4 py-2 font-semibold text-slate-950 bg-emerald-400 rounded hover:bg-emerald-300"
            >
              Open Today&apos;s Board
            </Link>
            <Link
              to="/pricing"
              className="px-4 py-2 border border-slate-600 rounded hover:border-emerald-300"
            >
              See plans
            </Link>
          </div>
        </section>

        {/* Simple FAQ stub */}
        <section className="pb-10 border-t border-slate-800 pt-7">
          <h2 className="mb-3 text-sm font-semibold">FAQ</h2>
          <div className="space-y-3 text-xs text-gray-300">
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
      <footer className="border-t border-slate-800 py-6">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-500">
            <p>Perplex Engine - Sports Betting Analytics</p>
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
