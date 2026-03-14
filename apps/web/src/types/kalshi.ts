export interface KalshiMarket {
    ticker: string;
    title: string;
    series_ticker: string;
    yes_bid: number;
    yes_ask: number;
    no_bid: number;
    no_ask: number;
    last_price: number;
    volume: number;
    open_interest: number;
    close_time: string;
}

export interface KalshiEVSignal {
    ticker: string;
    prop_label: string;
    player_name: string;
    sport: string;
    kalshi_prob: number;
    book_prob: number;
    edge: number;
    recommendation: "BUY YES" | "BUY NO" | "No Edge";
    book_name: string;
}

export interface KalshiArbAlert {
    ticker: string;
    player_name: string;
    kalshi_yes: number;
    book_no_implied: number;
    profit_margin: number;
    yes_stake: number;
    no_stake: number;
}

export interface KalshiOrder {
    ticker: string;
    side: "yes" | "no";
    count: number;
    price: number;
    type: "limit" | "market";
}

export interface KalshiPortfolio {
    balance: number;
    positions: {
        ticker: string;
        title: string;
        side: "yes" | "no";
        count: number;
        avg_cost: number;
        current_value: number;
        pnl: number;
    }[];
}
