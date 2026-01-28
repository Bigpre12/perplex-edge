import { useState } from 'react'
import { SportProvider } from './context/SportContext'
import {
  TopNav,
  Tabs,
  PlayerPropsTab,
  GameLinesTab,
} from './components'

const TABS = [
  { id: 'player-props', label: 'Player Props' },
  { id: 'game-lines', label: 'Game Lines' },
]

function App() {
  const [activeTab, setActiveTab] = useState('player-props')

  return (
    <SportProvider>
      <div className="min-h-screen bg-gray-900">
        <TopNav />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Tabs tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="mt-6">
            {activeTab === 'player-props' ? <PlayerPropsTab /> : <GameLinesTab />}
          </div>
        </main>
      </div>
    </SportProvider>
  )
}

export default App
