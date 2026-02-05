import { Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ToastProvider } from './context/ToastContext'
import { SportProvider } from './context/SportContext'
import { LandingPage, TodayDashboard, MyEdgePage, PricingPage } from './pages'
import {
  TopNav,
  PlayerPropsTab,
  GameLinesTab,
  StatsDashboard,
  MultiSportSlate,
  AnalyticsDashboard,
  BacktestTab,
  LiveEVFeed,
  ModelPerformance,
  AdminDashboard,
} from './components'
import { HundredPercentTab } from './components/HundredPercentTab'
import { ParlayBuilder } from './components/ParlayBuilder'
import { MyBetsTab } from './components/MyBetsTab'
import { FreshnessBanner } from './components/FreshnessBanner'
import { useAutoRefresh, formatTimeRemaining, formatLastUpdated } from './hooks/useAutoRefresh'

// Layout wrapper for app pages (with nav and controls)
function AppLayout({ children }: { children: React.ReactNode }) {
  const {
    isEnabled: autoRefreshEnabled,
    toggle: toggleAutoRefresh,
    lastUpdated,
    refresh: manualRefresh,
    nextRefreshIn,
  } = useAutoRefresh({ interval: 5 * 60 * 1000 })

  return (
    <div className="min-h-screen bg-gray-900">
      <TopNav />
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Auto-Refresh Controls + Freshness Banner */}
        <div className="flex items-center justify-end gap-4 mb-6 text-sm">
          {/* Data Freshness Banner */}
          <FreshnessBanner />
          
          {/* Last Updated */}
          <div className="text-gray-400 hidden lg:block">
            <span className="hidden sm:inline">Updated: </span>
            <span className="text-gray-300">{formatLastUpdated(lastUpdated)}</span>
          </div>
          
          {/* Next Refresh Countdown */}
          {autoRefreshEnabled && (
            <div className="text-gray-400">
              <span className="hidden sm:inline">Next: </span>
              <span className="text-blue-400">{formatTimeRemaining(nextRefreshIn)}</span>
            </div>
          )}
          
          {/* Manual Refresh Button */}
          <button
            onClick={manualRefresh}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Refresh now"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          {/* Auto-Refresh Toggle */}
          <div className="flex items-center gap-2">
            <span className="text-gray-400 hidden sm:inline">Auto</span>
            <button
              onClick={toggleAutoRefresh}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoRefreshEnabled ? 'bg-blue-600' : 'bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoRefreshEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
        
        {/* Page Content */}
        {children}
      </main>
      
      {/* Footer */}
      <footer className="border-t border-gray-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
            <p>Smart Parlay Builder by Perplex Edge</p>
            <div className="flex items-center gap-4">
              <span className={`flex items-center gap-1 ${autoRefreshEnabled ? 'text-green-400' : 'text-gray-500'}`}>
                <span className={`w-2 h-2 rounded-full ${autoRefreshEnabled ? 'bg-green-400' : 'bg-gray-600'}`}></span>
                {autoRefreshEnabled ? 'Live' : 'Paused'}
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Main App with Routes
function App() {
  return (
    <ErrorBoundary>
    <ToastProvider>
    <SportProvider>
      <Routes>
        {/* Landing page - no nav */}
        <Route path="/" element={<LandingPage />} />
        
        {/* App pages with nav layout */}
        <Route path="/today" element={
          <AppLayout>
            <TodayDashboard />
          </AppLayout>
        } />
        
        <Route path="/props" element={
          <AppLayout>
            <PlayerPropsTab />
          </AppLayout>
        } />
        
        <Route path="/game-lines" element={
          <AppLayout>
            <GameLinesTab />
          </AppLayout>
        } />
        
        <Route path="/stats" element={
          <AppLayout>
            <StatsDashboard />
          </AppLayout>
        } />
        
        <Route path="/parlay" element={
          <AppLayout>
            <ParlayBuilder />
          </AppLayout>
        } />
        
        <Route path="/my-bets" element={
          <AppLayout>
            <MyBetsTab />
          </AppLayout>
        } />
        
        <Route path="/my-edge" element={
          <AppLayout>
            <MyEdgePage />
          </AppLayout>
        } />
        
        <Route path="/pricing" element={<PricingPage />} />
        
        <Route path="/all-sports" element={
          <AppLayout>
            <MultiSportSlate />
          </AppLayout>
        } />
        
        <Route path="/live-ev" element={
          <AppLayout>
            <LiveEVFeed />
          </AppLayout>
        } />
        
        <Route path="/100-hits" element={
          <AppLayout>
            <HundredPercentTab />
          </AppLayout>
        } />
        
        <Route path="/model-performance" element={
          <AppLayout>
            <ModelPerformance />
          </AppLayout>
        } />
        
        <Route path="/analytics" element={
          <AppLayout>
            <AnalyticsDashboard />
          </AppLayout>
        } />
        
        <Route path="/backtest" element={
          <AppLayout>
            <BacktestTab />
          </AppLayout>
        } />
        
        <Route path="/admin" element={
          <AppLayout>
            <AdminDashboard />
          </AppLayout>
        } />
        
        {/* Catch-all redirect to landing */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </SportProvider>
    </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
