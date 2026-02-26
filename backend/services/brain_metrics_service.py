"""
Brain Metrics Service - Continuously updates brain_business_metrics table
"""
import asyncio
import asyncpg
import os
import psutil
import time
from datetime import datetime, timezone
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainMetricsService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.running = False
        
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network stats (simplified)
            network = psutil.net_io_counters()
            
            return {
                'cpu_usage': cpu_percent / 100.0,
                'memory_usage': memory.percent / 100.0,
                'disk_usage': disk.percent / 100.0,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'cpu_usage': 0.5,
                'memory_usage': 0.5,
                'disk_usage': 0.5,
                'network_bytes_sent': 0,
                'network_bytes_recv': 0
            }
    
    async def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics (simulated for now)"""
        try:
            # In a real implementation, these would come from your business logic
            # For now, we'll simulate some realistic values
            
            import random
            
            return {
                'total_recommendations': random.randint(50, 200),
                'recommendation_hit_rate': random.uniform(0.45, 0.65),
                'average_ev': random.uniform(0.05, 0.25),
                'clv_trend': random.uniform(-0.1, 0.3),
                'prop_volume': random.randint(100, 500),
                'user_confidence_score': random.uniform(0.7, 0.95),
                'api_response_time_ms': random.randint(50, 300),
                'error_rate': random.uniform(0.01, 0.05),
                'throughput': random.uniform(10, 50)
            }
        except Exception as e:
            logger.error(f"Error getting business metrics: {e}")
            return {
                'total_recommendations': 0,
                'recommendation_hit_rate': 0.0,
                'average_ev': 0.0,
                'clv_trend': 0.0,
                'prop_volume': 0,
                'user_confidence_score': 0.0,
                'api_response_time_ms': 0,
                'error_rate': 0.0,
                'throughput': 0.0
            }
    
    async def update_metrics(self):
        """Update metrics in database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get current metrics
            system_metrics = await self.get_system_metrics()
            business_metrics = await self.get_business_metrics()
            
            # Combine all metrics
            all_metrics = {**system_metrics, **business_metrics}
            
            # Insert into database
            await conn.execute("""
                INSERT INTO brain_business_metrics (
                    timestamp, total_recommendations, recommendation_hit_rate, average_ev,
                    clv_trend, prop_volume, user_confidence_score, api_response_time_ms,
                    error_rate, throughput, cpu_usage, memory_usage, disk_usage
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """, 
                datetime.now(timezone.utc),
                all_metrics['total_recommendations'],
                all_metrics['recommendation_hit_rate'],
                all_metrics['average_ev'],
                all_metrics['clv_trend'],
                all_metrics['prop_volume'],
                all_metrics['user_confidence_score'],
                all_metrics['api_response_time_ms'],
                all_metrics['error_rate'],
                all_metrics['throughput'],
                all_metrics['cpu_usage'],
                all_metrics['memory_usage'],
                all_metrics['disk_usage']
            )
            
            await conn.close()
            
            logger.info(f"Metrics updated: {all_metrics['total_recommendations']} recommendations, "
                       f"{all_metrics['recommendation_hit_rate']:.2%} hit rate")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def start_metrics_collection(self, interval_seconds: int = 300):
        """Start continuous metrics collection"""
        self.running = True
        logger.info(f"Starting metrics collection every {interval_seconds} seconds")
        
        while self.running:
            try:
                await self.update_metrics()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop metrics collection"""
        self.running = False
        logger.info("Stopping metrics collection")

# Global instance
metrics_service = BrainMetricsService()

async def get_current_metrics() -> Dict[str, Any]:
    """Get current metrics for API endpoints"""
    try:
        conn = await asyncpg.connect(metrics_service.db_url)
        
        # Get latest metrics
        latest = await conn.fetchrow("""
            SELECT * FROM brain_business_metrics 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        await conn.close()
        
        if latest:
            return dict(latest)
        else:
            return {}
            
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        return {}

async def get_metrics_summary(hours: int = 24) -> Dict[str, Any]:
    """Get metrics summary for the last N hours"""
    try:
        conn = await asyncpg.connect(metrics_service.db_url)
        
        # Get metrics for the last N hours
        since_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        metrics = await conn.fetch("""
            SELECT * FROM brain_business_metrics 
            WHERE timestamp >= $1
            ORDER BY timestamp DESC
        """, since_time)
        
        await conn.close()
        
        if not metrics:
            return {}
        
        # Calculate summary statistics
        total_recs = [m['total_recommendations'] for m in metrics]
        hit_rates = [m['recommendation_hit_rate'] for m in metrics]
        evs = [m['average_ev'] for m in metrics]
        
        return {
            'period_hours': hours,
            'total_records': len(metrics),
            'total_recommendations': sum(total_recs),
            'average_hit_rate': sum(hit_rates) / len(hit_rates),
            'average_ev': sum(evs) / len(evs),
            'max_hit_rate': max(hit_rates),
            'min_hit_rate': min(hit_rates),
            'latest_metrics': dict(metrics[0]) if metrics else {}
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        return {}

if __name__ == "__main__":
    # Test the metrics service
    async def test():
        await metrics_service.update_metrics()
        print("Test update completed")
    
    asyncio.run(test())
