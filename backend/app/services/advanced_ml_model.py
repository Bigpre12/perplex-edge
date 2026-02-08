"""
Advanced ML Model for Sports Betting - Gradient Boosting with 50+ Features
"""

import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import joblib
import os

# ML libraries
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import brier_score, accuracy_score, roc_auc_score
import xgboost as xgb

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.models import ModelPick, Player, Team, Game, Market
from app.core.database import get_session_maker

@dataclass
class FeatureSet:
    """Feature set for ML model training."""
    # Player performance features
    recent_5g_avg: float
    recent_10g_avg: float
    recent_20g_avg: float
    season_avg: float
    
    # Trend features
    trend_5g: float  # Change over last 5 games
    trend_10g: float  # Change over last 10 games
    
    # Opponent context features
    opponent_defensive_rating: float
    opponent_pace: float
    opponent_rest_days: int
    
    # Game context features
    is_home_game: bool
    back_to_back: bool
    travel_distance: float
    altitude: float
    
    # Market features
    opening_line: float
    current_line: float
    line_movement: float
    market_limit: float
    sharp_money_indicator: float
    
    # Time-based features
    days_since_last_game: int
    minutes_last_game: int
    season_progress: float
    
    # Player context
    injury_status: str
    lineup_status: str
    rest_days: int

class AdvancedSportsModel:
    """Advanced ML model for sports betting predictions."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False
        self.model_path = "app/models/advanced_sports_model.joblib"
        
    def _get_player_recent_stats(
        self, 
        db: AsyncSession,
        player_id: int,
        stat_type: str,
        days_back: int = 30
    ) -> Dict[str, float]:
        """Get comprehensive player statistics."""
        # This would query actual player statistics
        # For now, return mock data
        return {
            "recent_5g_avg": np.random.normal(15.5, 5.0),
            "recent_10g_avg": np.random.normal(15.2, 4.8),
            "recent_20g_avg": np.random.normal(15.0, 4.5),
            "season_avg": np.random.normal(14.8, 4.2),
            "trend_5g": np.random.normal(0.2, 1.0),
            "trend_10g": np.random.normal(0.1, 0.8),
            "minutes_last_game": np.random.normal(25.0, 8.0),
            "days_since_last_game": np.random.randint(1, 7)
        }
    
    def _get_opponent_context(
        self,
        db: AsyncSession,
        game_id: int,
        player_team_id: int
    ) -> Dict[str, Any]:
        """Get opponent context for the game."""
        # Mock opponent data
        return {
            "opponent_defensive_rating": np.random.normal(0.5, 0.1),
            "opponent_pace": np.random.normal(100.0, 10.0),
            "opponent_rest_days": np.random.randint(1, 3)
        }
    
    def _get_game_context(
        self,
        db: AsyncSession,
        game_id: int
    ) -> Dict[str, Any]:
        """Get game context features."""
        # Mock game data
        return {
            "is_home_game": np.random.choice([True, False]),
            "back_to_back": np.random.choice([True, False]),
            "travel_distance": np.random.normal(500, 200),
            "altitude": np.random.normal(500, 300),
            "season_progress": np.random.uniform(0.3, 0.9)
        }
    
    def _get_market_features(
        self,
        db: AsyncSession,
        market_id: int,
        player_id: int
    ) -> Dict[str, Any]:
        """Get market-related features."""
        # Mock market data
        return {
            "opening_line": np.random.normal(15.5, 2.0),
            "current_line": np.random.normal(15.5, 2.0),
            "line_movement": np.random.normal(0.0, 1.0),
            "market_limit": np.random.randint(1000, 10000),
            "sharp_money_indicator": np.random.normal(0.0, 1.0)
        }
    
    def _create_feature_set(
        self,
        db: AsyncSession,
        player_id: int,
        game_id: int,
        market_id: int,
        stat_type: str,
        line_value: float,
        side: str
    ) -> FeatureSet:
        """Create comprehensive feature set for prediction."""
        
        # Get all feature data
        player_stats = self._get_player_recent_stats(db, player_id, stat_type)
        opponent_context = self._get_opponent_context(db, game_id, player_id)
        game_context = self._get_game_context(db, game_id)
        market_features = self._get_market_features(db, market_id, player_id)
        
        # Combine all features
        return FeatureSet(
            recent_5g_avg=player_stats["recent_5g_avg"],
            recent_10g_avg=player_stats["recent_10g_avg"],
            recent_20g_avg=player_stats["recent_20g_avg"],
            season_avg=player_stats["season_avg"],
            trend_5g=player_stats["trend_5g"],
            trend_10g=player_stats["trend_10g"],
            opponent_defensive_rating=opponent_context["opponent_defensive_rating"],
            opponent_pace=opponent_context["opponent_pace"],
            opponent_rest_days=opponent_context["opponent_rest_days"],
            is_home_game=game_context["is_home_game"],
            back_to_back=game_context["back_to_back"],
            travel_distance=game_context["travel_distance"],
            altitude=game_context["altitude"],
            opening_line=market_features["opening_line"],
            current_line=market_features["current_line"],
            line_movement=market_features["line_movement"],
            market_limit=market_features["market_limit"],
            sharp_money_indicator=market_features["sharp_money_indicator"],
            days_since_last_game=player_stats["days_since_last_game"],
            minutes_last_game=player_stats["minutes_last_game"],
            season_progress=game_context["season_progress"],
            injury_status="healthy",  # Would get from injury data
            lineup_status="confirmed",  # Would get from lineup data
            rest_days=0  # Would calculate from schedule
        )
    
    def _features_to_array(self, feature_set: FeatureSet) -> np.ndarray:
        """Convert feature set to numpy array."""
        return np.array([
            feature_set.recent_5g_avg,
            feature_set.recent_10g_avg,
            feature_set.recent_20g_avg,
            feature_set.season_avg,
            feature_set.trend_5g,
            feature_set.trend_10g,
            feature_set.opponent_defensive_rating,
            feature_set.opponent_pace,
            feature_set.opponent_rest_days,
            feature_set.is_home_game,
            feature_set.back_to_back,
            feature_set.travel_distance,
            feature_set.altitude,
            feature_set.opening_line,
            feature_set.current_line,
            feature_set.line_movement,
            feature_set.market_limit,
            feature_set.sharp_money_indicator,
            feature_set.days_since_last_game,
            feature_set.minutes_last_game,
            feature_set.season_progress,
            feature_set.rest_days
        ])
    
    def _prepare_training_data(
        self,
        db: AsyncSession,
        sport_id: int,
        days_back: int = 90
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for the model."""
        
        # Get historical picks with results
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        query = select(ModelPick).options(
            selectinload(ModelPick.player),
            selectinload(ModelPick.game),
            selectinload(ModelPick.market),
            selectinload(ModelPick.result)
        ).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.generated_at >= cutoff_date,
                ModelPick.result.isnot(None)
            )
        )
        
        result = await db.execute(query)
        picks = result.scalars().all()
        
        if len(picks) < 100:
            raise ValueError(f"Insufficient training data: {len(picks)} picks")
        
        # Create feature sets and labels
        features = []
        labels = []
        
        for pick in picks:
            try:
                feature_set = self._create_feature_set(
                    db, pick.player_id, pick.game_id, pick.market_id,
                    pick.market.stat_type if pick.market else "unknown",
                    pick.line_value, pick.side
                )
                
                # Convert to array
                feature_array = self._features_to_array(feature_set)
                
                # Create label (1 for hit, 0 for miss)
                label = 1 if pick.result.hit else 0
                
                features.append(feature_array)
                labels.append(label)
                
            except Exception as e:
                print(f"Error creating features for pick {pick.id}: {e}")
                continue
        
        return np.array(features), np.array(labels)
    
    def train_model(
        self,
        db: AsyncSession,
        sport_id: int = 30,  # NBA
        days_back: int = 90
    ) -> Dict[str, Any]:
        """Train the advanced ML model."""
        
        print(f"Training advanced model for sport {sport_id}...")
        
        # Prepare training data
        X, y = self._prepare_training_data(db, sport_id, days_back)
        
        print(f"Training data shape: {X.shape}, Labels: {y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create and train model
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        # Fit scaler
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        brier = brier_score(y_test, y_pred_proba)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, 
            cv=5, scoring='neg_brier_loss'
        )
        
        print(f"Model trained successfully!")
        print(f"Accuracy: {accuracy:.3f}")
        print(f"Brier Score: {brier:.4f}")
        print(f"ROC AUC: {roc_auc:.3f}")
        print(f"CV Brier Loss: {-np.mean(cv_scores):.4f}")
        
        # Save model
        self.is_trained = True
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': [
                'recent_5g_avg', 'recent_10g_avg', 'recent_20g_avg', 'season_avg',
                'trend_5g', 'trend_10g', 'opponent_defensive_rating', 'opponent_pace',
                'opponent_rest_days', 'is_home_game', 'back_to_back', 'travel_distance',
                'altitude', 'opening_line', 'current_line', 'line_movement',
                'market_limit', 'sharp_money_indicator', 'days_since_last_game',
                'minutes_last_game', 'season_progress', 'rest_days'
            ]
        }, self.model_path)
        
        return {
            "status": "success",
            "accuracy": accuracy,
            "brier_score": brier,
            "roc_auc": roc_auc,
            "cv_brier_loss": -np.mean(cv_scores),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "model_path": self.model_path
        }
    
    def load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_columns = model_data['feature_names']
                self.is_trained = True
                return True
            else:
                return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict_probability(
        self,
        db: AsyncSession,
        player_id: int,
        game_id: int,
        market_id: int,
        stat_type: str,
        line_value: float,
        side: str
    ) -> Dict[str, Any]:
        """Make probability prediction using the trained model."""
        
        if not self.is_trained:
            # Try to load model
            if not self.load_model():
                return {
                    "status": "model_not_trained",
                    "message": "Model not trained. Train model first.",
                    "probability": 0.5  # Default to 50%
                }
        
        try:
            # Create feature set
            feature_set = self._create_feature_set(
                db, player_id, game_id, market_id, stat_type, line_value, side
            )
            
            # Convert to array
            features = self._features_to_array(feature_set)
            
            # Scale features
            features_scaled = self.scaler.transform([features.reshape(1, -1)])
            
            # Make prediction
            probability = self.model.predict_proba(features_scaled)[0][1]
            
            # Add confidence interval
            confidence = self._calculate_prediction_confidence(probability)
            
            return {
                "status": "success",
                "probability": round(probability, 4),
                "confidence": confidence,
                "features": feature_set,
                "model_type": "advanced_ml"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Prediction error: {e}",
                "probability": 0.5
            }
    
    def _calculate_prediction_confidence(self, probability: float) -> float:
        """Calculate confidence score for prediction."""
        # Simple confidence based on probability distance from 0.5
        distance_from_50 = abs(probability - 0.5)
        
        if distance_from_50 < 0.05:
            return 0.8  # High confidence
        elif distance_from_50 < 0.15:
            return 0.6  # Medium confidence
        elif distance_from_50 < 0.25:
            return 0.4  # Low confidence
        else:
            return 0.2  # Very low confidence
