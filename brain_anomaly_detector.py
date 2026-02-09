"""
Brain Anomaly Detection Service - Detects and tracks anomalies in brain metrics
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainAnomalyDetector:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.thresholds = {
            'error_rate': {'warning': 0.05, 'critical': 0.10},  # 5%, 10%
            'recommendation_hit_rate': {'warning': 0.45, 'critical': 0.35},  # Below 45%, 35%
            'api_response_time_ms': {'warning': 200, 'critical': 500},  # 200ms, 500ms
            'cpu_usage': {'warning': 0.80, 'critical': 0.90},  # 80%, 90%
            'memory_usage': {'warning': 0.85, 'critical': 0.95},  # 85%, 95%
            'throughput': {'warning': 15.0, 'critical': 10.0},  # Below 15, 10 req/s
            'average_ev': {'warning': 0.05, 'critical': -0.05},  # Below 5%, -5%
            'user_confidence_score': {'warning': 0.70, 'critical': 0.60},  # Below 70%, 60%
        }
        
    async def get_baseline_values(self, metric_name: str, hours: int = 24) -> Optional[float]:
        """Get baseline value for a metric from historical data"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get average value from the last N hours
            result = await conn.fetchval("""
                SELECT AVG(CASE 
                    WHEN metric_name = $1 THEN current_value 
                    ELSE NULL 
                END) as avg_value
                FROM brain_business_metrics 
                WHERE timestamp >= NOW() - INTERVAL '$2 hours'
            """, metric_name, hours)
            
            await conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting baseline for {metric_name}: {e}")
            return None
    
    async def get_current_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get latest value
            result = await conn.fetchval("""
                SELECT CASE 
                    WHEN metric_name = $1 THEN current_value 
                    ELSE NULL 
                END as current_value
                FROM brain_business_metrics 
                WHERE metric_name = $1
                ORDER BY timestamp DESC 
                LIMIT 1
            """, metric_name)
            
            await conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting current value for {metric_name}: {e}")
            return None
    
    def calculate_change_percentage(self, baseline: float, current: float) -> float:
        """Calculate percentage change from baseline"""
        if baseline == 0:
            return 0.0
        return ((current - baseline) / baseline) * 100
    
    def determine_severity(self, metric_name: str, current_value: float) -> str:
        """Determine anomaly severity based on thresholds"""
        thresholds = self.thresholds.get(metric_name, {})
        
        if 'critical' in thresholds:
            if metric_name in ['recommendation_hit_rate', 'throughput', 'average_ev', 'user_confidence_score']:
                # Lower values are worse for these metrics
                if current_value <= thresholds['critical']:
                    return 'high'
                elif current_value <= thresholds['warning']:
                    return 'medium'
            else:
                # Higher values are worse for these metrics
                if current_value >= thresholds['critical']:
                    return 'high'
                elif current_value >= thresholds['warning']:
                    return 'medium'
        
        return 'low'
    
    async def detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in current metrics"""
        anomalies = []
        
        # Get current metrics
        current_metrics = await self.get_all_current_metrics()
        
        for metric_name, current_value in current_metrics.items():
            if current_value is None:
                continue
            
            # Get baseline
            baseline = await self.get_baseline_values(metric_name)
            if baseline is None:
                continue
            
            # Calculate change percentage
            change_pct = self.calculate_change_percentage(baseline, current_value)
            
            # Determine severity
            severity = self.determine_severity(metric_name, current_value)
            
            # Check if this is an anomaly (significant change or threshold breach)
            is_anomaly = (
                abs(change_pct) > 20.0 or  # More than 20% change
                severity in ['high', 'medium']  # Threshold breach
            )
            
            if is_anomaly:
                anomaly = {
                    'metric_name': metric_name,
                    'baseline_value': baseline,
                    'current_value': current_value,
                    'change_pct': change_pct,
                    'severity': severity,
                    'details': self.generate_anomaly_details(metric_name, baseline, current_value, change_pct)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def generate_anomaly_details(self, metric_name: str, baseline: float, current: float, change_pct: float) -> str:
        """Generate human-readable anomaly details"""
        direction = "increased" if current > baseline else "decreased"
        
        details_map = {
            'error_rate': f"API error rate {direction} from {baseline:.2%} to {current:.2%} ({abs(change_pct):.1f}% change)",
            'recommendation_hit_rate': f"Recommendation hit rate {direction} from {baseline:.2%} to {current:.2%} ({abs(change_pct):.1f}% change)",
            'api_response_time_ms': f"API response time {direction} from {baseline:.0f}ms to {current:.0f}ms ({abs(change_pct):.1f}% change)",
            'cpu_usage': f"CPU usage {direction} from {baseline:.1%} to {current:.1%} ({abs(change_pct):.1f}% change)",
            'memory_usage': f"Memory usage {direction} from {baseline:.1%} to {current:.1%} ({abs(change_pct):.1f}% change)",
            'throughput': f"Throughput {direction} from {baseline:.1f} to {current:.1f} req/s ({abs(change_pct):.1f}% change)",
            'average_ev': f"Average EV {direction} from {baseline:.2%} to {current:.2%} ({abs(change_pct):.1f}% change)",
            'user_confidence_score': f"User confidence {direction} from {baseline:.2%} to {current:.2%} ({abs(change_pct):.1f}% change)",
            'prop_volume': f"Prop volume {direction} from {baseline:.0f} to {current:.0f} ({abs(change_pct):.1f}% change)"
        }
        
        return details_map.get(metric_name, f"Metric {metric_name} {direction} by {abs(change_pct):.1f}%")
    
    async def get_all_current_metrics(self) -> Dict[str, float]:
        """Get all current metric values"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get latest metrics
            result = await conn.fetch("""
                SELECT metric_name, current_value
                FROM brain_business_metrics 
                WHERE timestamp = (
                    SELECT MAX(timestamp) FROM brain_business_metrics
                )
            """)
            
            await conn.close()
            
            return {row['metric_name']: row['current_value'] for row in result}
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}
    
    async def record_anomaly(self, anomaly: Dict) -> bool:
        """Record an anomaly in the database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Check if similar anomaly already exists and is active
            existing = await conn.fetchval("""
                SELECT id FROM brain_anomalies 
                WHERE metric_name = $1 
                AND status = 'active'
                AND timestamp > NOW() - INTERVAL '1 hour'
            """, anomaly['metric_name'])
            
            if existing:
                logger.info(f"Anomaly for {anomaly['metric_name']} already active")
                await conn.close()
                return False
            
            # Insert new anomaly
            await conn.execute("""
                INSERT INTO brain_anomalies (
                    metric_name, baseline_value, current_value, change_pct,
                    severity, status, details
                ) VALUES ($1, $2, $3, $4, $5, 'active', $6)
            """, 
                anomaly['metric_name'],
                anomaly['baseline_value'],
                anomaly['current_value'],
                anomaly['change_pct'],
                anomaly['severity'],
                anomaly['details']
            )
            
            await conn.close()
            logger.info(f"Recorded anomaly: {anomaly['metric_name']} - {anomaly['severity']}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording anomaly: {e}")
            return False
    
    async def run_anomaly_detection(self):
        """Run anomaly detection and record findings"""
        try:
            logger.info("Running anomaly detection...")
            
            # Detect anomalies
            anomalies = await self.detect_anomalies()
            
            if anomalies:
                logger.info(f"Found {len(anomalies)} anomalies")
                
                for anomaly in anomalies:
                    await self.record_anomaly(anomaly)
            else:
                logger.info("No anomalies detected")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return []
    
    async def get_active_anomalies(self) -> List[Dict]:
        """Get all active anomalies"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetch("""
                SELECT * FROM brain_anomalies 
                WHERE status = 'active'
                ORDER BY 
                    CASE severity 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    timestamp DESC
            """)
            
            await conn.close()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting active anomalies: {e}")
            return []
    
    async def resolve_anomaly(self, anomaly_id: int, resolution_method: str) -> bool:
        """Mark an anomaly as resolved"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute("""
                UPDATE brain_anomalies 
                SET status = 'resolved', 
                    resolved_at = NOW(),
                    resolution_method = $1
                WHERE id = $2
            """, resolution_method, anomaly_id)
            
            await conn.close()
            logger.info(f"Resolved anomaly {anomaly_id}: {resolution_method}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving anomaly: {e}")
            return False

# Global instance
anomaly_detector = BrainAnomalyDetector()

async def run_anomaly_check():
    """Run a single anomaly check"""
    return await anomaly_detector.run_anomaly_detection()

async def get_active_anomalies():
    """Get active anomalies for API endpoints"""
    return await anomaly_detector.get_active_anomalies()

if __name__ == "__main__":
    # Test anomaly detection
    async def test():
        anomalies = await run_anomaly_check()
        print(f"Detected {len(anomalies)} anomalies")
        for anomaly in anomalies:
            print(f"  - {anomaly['metric_name']}: {anomaly['change_pct']:.1f}% ({anomaly['severity']})")
    
    asyncio.run(test())
