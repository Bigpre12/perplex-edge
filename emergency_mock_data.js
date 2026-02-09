// EMERGENCY MOCK DATA FOR SUPER BOWL
// Use this if endpoints are not working

const mockSuperBowlProps = [
  {
    id: 1,
    player: { 
      id: 1001,
      name: "Drake Maye", 
      position: "QB" 
    },
    market: { 
      id: 2001,
      stat_type: "Passing Yards", 
      description: "Over/Under Passing Yards" 
    },
    side: "over",
    line_value: 245.5,
    odds: -110,
    model_probability: 0.55,
    implied_probability: 0.52,
    expected_value: 0.12,
    confidence_score: 0.85,
    edge: 0.12,
    generated_at: "2026-02-08T17:00:00Z"
  },
  {
    id: 2,
    player: { 
      id: 1002,
      name: "Sam Darnold", 
      position: "QB" 
    },
    market: { 
      id: 2002,
      stat_type: "Passing Yards", 
      description: "Over/Under Passing Yards" 
    },
    side: "over",
    line_value: 235.5,
    odds: -105,
    model_probability: 0.53,
    implied_probability: 0.51,
    expected_value: 0.08,
    confidence_score: 0.78,
    edge: 0.08,
    generated_at: "2026-02-08T17:00:00Z"
  },
  {
    id: 3,
    player: { 
      id: 1003,
      name: "Drake Maye", 
      position: "QB" 
    },
    market: { 
      id: 2003,
      stat_type: "Passing TDs", 
      description: "Over/Under Passing TDs" 
    },
    side: "over",
    line_value: 1.5,
    odds: -115,
    model_probability: 0.58,
    implied_probability: 0.53,
    expected_value: 0.15,
    confidence_score: 0.82,
    edge: 0.15,
    generated_at: "2026-02-08T17:00:00Z"
  },
  {
    id: 4,
    player: { 
      id: 1004,
      name: "Sam Darnold", 
      position: "QB" 
    },
    market: { 
      id: 2004,
      stat_type: "Passing TDs", 
      description: "Over/Under Passing TDs" 
    },
    side: "over",
    line_value: 1.5,
    odds: -110,
    model_probability: 0.56,
    implied_probability: 0.52,
    expected_value: 0.12,
    confidence_score: 0.75,
    edge: 0.12,
    generated_at: "2026-02-08T17:00:00Z"
  },
  {
    id: 5,
    player: { 
      id: 1005,
      name: "Drake Maye", 
      position: "QB" 
    },
    market: { 
      id: 2005,
      stat_type: "Completions", 
      description: "Over/Under Completions" 
    },
    side: "over",
    line_value: 22.5,
    odds: -105,
    model_probability: 0.54,
    implied_probability: 0.51,
    expected_value: 0.09,
    confidence_score: 0.73,
    edge: 0.09,
    generated_at: "2026-02-08T17:00:00Z"
  }
];

// Emergency API function
export const getEmergencySuperBowlProps = async () => {
  // Try real endpoints first
  try {
    const response = await fetch('https://railway-engine-production.up.railway.app/clean/super-bowl-props');
    if (response.ok) {
      const data = await response.json();
      return data;
    }
  } catch (error) {
    console.log('Clean endpoint failed, using mock data');
  }
  
  // Fallback to mock data
  return {
    items: mockSuperBowlProps,
    total: mockSuperBowlProps.length,
    timestamp: new Date().toISOString()
  };
};

// Frontend usage:
// const { items } = await getEmergencySuperBowlProps();
