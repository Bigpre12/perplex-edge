import { useState } from 'react'
import { SportProvider, useSportContext } from './context/SportContext'
import {
  TopNav,
  Tabs,
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

const TABS = [
  { id: 'multi-sport', label: '🎯 All Sports' },
  { id: 'live-ev', label: '🔴 Live EV' },
  { id: 'player-props', label: 'Player Props' },
  { id: 'game-lines', label: 'Game Lines' },
  { id: '100pct-hits', label: '100% Hit Rate' },
  { id: 'parlay-builder', label: 'Parlay Builder' },
  { id: 'my-bets', label: 'My Bets' },
  { id: 'model-perf', label: '📈 Model Performance' },
  { id: 'analytics', label: '📊 Analytics' },
  { id: 'backtest', label: '🔬 Backtest' },
  { id: 'stats', label: 'Stats' },
  { id: 'admin', label: '⚙️ Admin' },
]

// Loading spinner component
function LoadingSpinner({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64">
      <div className="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
      <p className="text-gray-400">{message}</p>
    </div>
  );
}

// Error display component
function ErrorDisplay({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64">
      <div className="bg-red-900/20 border border-red-800 rounded-lg p-6 text-center">
        <p className="text-red-400 font-medium mb-2">Failed to load</p>
        <p className="text-gray-400 text-sm">{message}</p>
        <p className="text-gray-500 text-xs mt-2">Check browser console for details</p>
      </div>
    </div>
  );
}

// Inner app content that uses SportContext
function AppContent() {
  const [activeTab, setActiveTab] = useState('multi-sport')
  const { sportId, isLoading: sportLoading, error: sportError } = useSportContext();
  
  // Auto-refresh hook (5 minute interval)
  const {
    isEnabled: autoRefreshEnabled,
    toggle: toggleAutoRefresh,
    lastUpdated,
    refresh: manualRefresh,
    nextRefreshIn,
  } = useAutoRefresh({ interval: 5 * 60 * 1000 })

  // Render tab content with loading guard
  const renderTabContent = () => {
    // Show error if sport loading failed
    if (sportError) {
      return <ErrorDisplay message={sportError} />;
    }
    
    // Show loading while sport context initializes
    if (sportLoading || !sportId) {
      console.log('[App] Waiting for sport context:', { sportLoading, sportId });
      return <LoadingSpinner message="Loading sports data..." />;
    }
    
    console.log('[App] Rendering tab content with sportId:', sportId);
    
    // Render active tab
    switch (activeTab) {
      case 'multi-sport':
        return <MultiSportSlate />;
      case 'live-ev':
        return <LiveEVFeed />;
      case 'player-props':
        return <PlayerPropsTab />;
      case 'game-lines':
        return <GameLinesTab />;
      case '100pct-hits':
        return <HundredPercentTab />;
      case 'parlay-builder':
        return <ParlayBuilder />;
      case 'my-bets':
        return <MyBetsTab />;
      case 'model-perf':
        return <ModelPerformance />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'backtest':
        return <BacktestTab />;
      case 'stats':
        return <StatsDashboard />;
      case 'admin':
        return <AdminDashboard />;
      default:
        return <MultiSportSlate />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <TopNav />
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Tabs and Auto-Refresh Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <Tabs tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
          
          {/* Auto-Refresh Controls + Freshness Banner */}
          <div className="flex items-center gap-4 text-sm">
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
        </div>
        
        {/* Tab Content with Loading Guard */}
        <div>
          {renderTabContent()}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-gray-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
            <p>Perplex Engine - Sports Betting Analytics</p>
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

// Main App component wraps everything in providers
function App() {
  return (
    <SportProvider>
      <AppContent />
    </SportProvider>
  )
}

export default App
