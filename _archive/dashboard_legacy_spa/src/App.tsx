import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import PlayerProps from './pages/PlayerProps';
import Arbitrage from './pages/Arbitrage';
import ParlayBuilder from './pages/ParlayBuilder';
import SharedIntel from './pages/SharedIntel';
import TailLink from './pages/TailLink';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="player-props" element={<PlayerProps />} />
        <Route path="market-analysis" element={<Arbitrage />} />
        <Route path="parlay-builder" element={<ParlayBuilder />} />
        <Route path="shared-intel" element={<SharedIntel />} />
        <Route path="share/:id" element={<TailLink />} />

        {/* Redirect any unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
