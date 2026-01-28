import { useState } from 'react'
import { SportProvider } from './context/SportContext'
import {
  TopNav,
  Tabs,
  PlayerPropsTab,
  GameLinesTab,
  StatsDashboard,
} from './components'
import { useAutoRefresh, formatTimeRemaining, formatLastUpdated } from './hooks/useAutoRefresh'

const TABS = [
  { id: 'player-props', label: 'Player Props' },
  { id: 'game-lines', label: 'Game Lines' },
  { id: 'stats', label: 'Stats Dashboard' },
]

function App() {
  const [activeTab, setActiveTab] = useState('player-props')
  
  // Auto-refresh hook (5 minute interval)
  const {
    isEnabled: autoRefreshEnabled,
    toggle: toggleAutoRefresh,
    lastUpdated,
    refresh: manualRefresh,
    nextRefreshIn,
  } = useAutoRefresh({ interval: 5 * 60 * 1000 })

  return (
    <SportProvider>
      <div className="min-h-screen bg-gray-900">
        <TopNav />
        
        <main className="max-w-7xl mx-auto px-4 py-6">
          {/* Tabs and Auto-Refresh Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <Tabs tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
            
            {/* Auto-Refresh Controls */}
            <div className="flex items-center gap-4 text-sm">
              {/* Last Updated */}
              <div className="text-gray-400">
                <span className="hidden sm:inline">Last updated: </span>
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
          
          {/* Tab Content */}
          <div>
            {activeTab === 'player-props' && <PlayerPropsTab />}
            {activeTab === 'game-lines' && <GameLinesTab />}
            {activeTab === 'stats' && <StatsDashboard />}
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
    </SportProvider>
  )
}

export default App
