/**
 * LandingPage - Marketing home page with hero and feature sections.
 * 
 * Shows the value proposition of the app and drives users to the main dashboard.
 */

import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-gray-900 to-emerald-900/20" />
        
        <div className="relative max-w-7xl mx-auto px-4 py-24 sm:py-32">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6">
              Multi-Sport Player Prop Engine
            </h1>
            <p className="text-xl sm:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              EV calculations, hit-rate tracking, and smart parlay builder.
              <br />
              Make data-driven betting decisions across NBA, NFL, MLB, NHL, and more.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/today"
                className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold text-lg rounded-lg transition-colors shadow-lg shadow-blue-600/25"
              >
                See Today's Board
              </Link>
              <Link
                to="/props"
                className="px-8 py-4 bg-gray-700 hover:bg-gray-600 text-white font-bold text-lg rounded-lg transition-colors"
              >
                Browse Player Props
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Sections */}
      <section className="py-20 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white text-center mb-16">
            Everything You Need to Find Edge
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Player Props Feature */}
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
              <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Player Props</h3>
              <p className="text-gray-400 mb-4">
                EV-ranked player props with Kelly sizing, line movement tracking, and multi-book comparison.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Expected Value calculations
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Kelly Criterion bet sizing
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Alt-line explorer
                </li>
              </ul>
            </div>

            {/* Stats Feature */}
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
              <div className="w-12 h-12 bg-emerald-600/20 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Stats Dashboard</h3>
              <p className="text-gray-400 mb-4">
                Track hot and cold players, win/lose streaks, and hit-rate trends by market.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Hot/Cold player tracking
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Market-specific hit rates
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Trust score quality tags
                </li>
              </ul>
            </div>

            {/* Parlay Builder Feature */}
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
              <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Parlay Builder</h3>
              <p className="text-gray-400 mb-4">
                Build multi-sport and same-game parlays with combined EV and correlation analysis.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Multi-sport parlays
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Same-game parlay support
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">+</span> Combined EV calculations
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Sports Supported */}
      <section className="py-16 border-t border-gray-800 bg-gray-800/30">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            Sports Covered
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            {['NBA', 'NFL', 'MLB', 'NHL', 'NCAAB', 'NCAAF', 'ATP', 'WTA'].map((sport) => (
              <span
                key={sport}
                className="px-4 py-2 bg-gray-700 rounded-lg text-white font-medium"
              >
                {sport}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 border-t border-gray-800">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Start Finding Edge Today
          </h2>
          <p className="text-gray-400 mb-8">
            No sign-up required. Browse today's props and see the data for yourself.
          </p>
          <Link
            to="/today"
            className="inline-block px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold text-lg rounded-lg transition-colors shadow-lg shadow-blue-600/25"
          >
            View Today's Board
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
            <p>Perplex Engine - Sports Betting Analytics</p>
            <div className="flex gap-6">
              <Link to="/today" className="hover:text-white transition-colors">Today</Link>
              <Link to="/props" className="hover:text-white transition-colors">Props</Link>
              <Link to="/stats" className="hover:text-white transition-colors">Stats</Link>
              <Link to="/parlay" className="hover:text-white transition-colors">Parlay</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
