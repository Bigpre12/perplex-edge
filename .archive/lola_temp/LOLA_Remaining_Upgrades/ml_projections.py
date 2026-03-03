# backend/ml/projections.py
# Gradient Boosted Tree projection model
# pip install scikit-learn joblib
import os
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

MODEL_PATH = os.getenv('ML_MODEL_PATH', 'backend/ml/models')
os.makedirs(MODEL_PATH, exist_ok=True)

FEATURES = [
    'rolling_avg_5', 'rolling_avg_10', 'rolling_avg_20',
    'vs_opponent_avg', 'home_away_flag', 'days_rest',
    'is_b2b', 'dvp_rank', 'pace', 'minutes_avg_5'
]

def build_feature_vector(player_stats: dict) -> list:
    return [player_stats.get(f, 0.0) or 0.0 for f in FEATURES]

def train_model(sport: str, stat_category: str, db):
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error
    import joblib
    from models import PlayerStats

    cutoff = datetime.utcnow() - timedelta(days=365)
    records = db.query(PlayerStats).filter(
        PlayerStats.sport == sport,
        PlayerStats.stat_category == stat_category,
        PlayerStats.game_date >= cutoff
    ).all()
    if len(records) < 50:
        return {'status': 'insufficient_data', 'records': len(records)}
    X, y = [], []
    for r in records:
        features = build_feature_vector({
            'rolling_avg_5': r.rolling_avg_5, 'rolling_avg_10': r.rolling_avg_10,
            'rolling_avg_20': r.rolling_avg_20, 'vs_opponent_avg': r.vs_opponent_avg,
            'home_away_flag': 1 if r.is_home else 0,
            'days_rest': r.days_rest or 1, 'is_b2b': 1 if r.is_b2b else 0,
            'dvp_rank': r.dvp_rank or 15, 'pace': r.pace or 100, 'minutes_avg_5': r.minutes_avg_5 or 30
        })
        X.append(features)
        y.append(r.value)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    import joblib
    path = f'{MODEL_PATH}/{sport}_{stat_category}.pkl'
    joblib.dump(model, path)
    return {'status': 'trained', 'sport': sport, 'stat': stat_category,
            'records': len(records), 'mae': round(mae, 3), 'model_path': path}

def predict(sport: str, stat_category: str, player_features: dict) -> Optional[float]:
    import joblib
    path = f'{MODEL_PATH}/{sport}_{stat_category}.pkl'
    if not os.path.exists(path):
        return None
    model = joblib.load(path)
    vector = build_feature_vector(player_features)
    return round(float(model.predict([vector])[0]), 2)

def retrain_all(db):
    targets = [
        ('NBA','points'),('NBA','rebounds'),('NBA','assists'),('NBA','threes'),
        ('NFL','passing_yards'),('NFL','rushing_yards'),('NFL','receiving_yards'),
        ('MLB','hits'),('MLB','home_runs'),('NHL','goals'),('NHL','shots')
    ]
    results = []
    for sport, stat in targets:
        try:
            results.append(train_model(sport, stat, db))
        except Exception as e:
            results.append({'sport': sport, 'stat': stat, 'error': str(e)})
    return results
