import React from 'react';

const SPORTS = [
  { id: 'all', label: 'All', icon: '🌎' },
  { id: 'americanfootball_nfl', label: 'NFL', icon: '🏈' },
  { id: 'basketball_nba', label: 'NBA', icon: '🏀' },
  { id: 'baseball_mlb', label: 'MLB', icon: '⚾' },
  { id: 'icehockey_nhl', label: 'NHL', icon: '🏒' },
  { id: 'soccer_usa_mls', label: 'Soccer', icon: '⚽' },
];

interface SportFilterProps {
  activeSport: string;
  onSportChange: (id: string) => void;
}

export const SportFilter: React.FC<SportFilterProps> = ({ activeSport, onSportChange }) => {
  return (
    <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide py-4">
      {SPORTS.map((sport) => (
        <button
          key={sport.id}
          onClick={() => onSportChange(sport.id)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-full whitespace-nowrap transition-all ${
            activeSport === sport.id
              ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20 scale-105'
              : 'bg-white/5 text-white/60 hover:bg-white/10 border border-white/5'
          }`}
        >
          <span className="text-sm">{sport.icon}</span>
          <span className="text-sm font-medium">{sport.label}</span>
        </button>
      ))}
    </div>
  );
};
