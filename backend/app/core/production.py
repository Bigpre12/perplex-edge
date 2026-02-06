"""
Production-specific configuration and utilities.
Separates production concerns from development configuration.
"""

import os
from typing import List, Dict, Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class ProductionConfig:
    """Production configuration utilities and validation."""
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    @staticmethod
    def is_railway() -> bool:
        """Check if running on Railway platform."""
        return (
            bool(os.getenv("RAILWAY_ENVIRONMENT")) or 
            bool(os.getenv("RAILWAY_SERVICE_NAME")) or 
            bool(os.getenv("RAILWAY_PROJECT_NAME")) or
            "railway" in os.getenv("RAILWAY_ENVIRONMENT", "").lower() or
            "railway" in os.getenv("RAILWAY_SERVICE_NAME", "").lower() or
            "railway" in os.getenv("RAILWAY_PROJECT_NAME", "").lower()
        )
    
    @staticmethod
    def get_production_origins() -> List[str]:
        """Get production CORS origins from environment variables."""
        origins = []
        
        # Frontend URL
        frontend_url = os.getenv("FRONTEND_URL", "").strip()
        if frontend_url:
            origins.append(frontend_url)
        
        # Additional CORS origins
        cors_origins = os.getenv("CORS_ORIGINS", "").strip()
        if cors_origins:
            for origin in cors_origins.split(","):
                origin = origin.strip()
                if origin and origin not in origins:
                    origins.append(origin)
        
        return origins
    
    @staticmethod
    def get_development_origins() -> List[str]:
        """Get development CORS origins."""
        return [
            "http://localhost:5173",
            "http://localhost:3000", 
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000"
        ]
    
    @staticmethod
    def validate_production_config() -> Dict[str, Any]:
        """Validate production configuration."""
        issues = []
        warnings = []
        
        # Check required environment variables
        required_vars = [
            "ENVIRONMENT",
            "DATABASE_URL", 
            "ODDS_API_KEY",
            "FRONTEND_URL"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Check for development values in production
        if ProductionConfig.is_production():
            dev_values = ["localhost", "127.0.0.1", "development"]
            
            # Check database URL
            db_url = os.getenv("DATABASE_URL", "")
            if any(dev in db_url.lower() for dev in dev_values):
                issues.append("DATABASE_URL contains development values in production")
            
            # Check frontend URL
            frontend_url = os.getenv("FRONTEND_URL", "")
            if any(dev in frontend_url.lower() for dev in dev_values):
                issues.append("FRONTEND_URL contains development values in production")
            
            # Check for hardcoded API keys (basic pattern)
            api_key = os.getenv("ODDS_API_KEY", "")
            suspicious_keys = ["your_", "test_", "demo_", "example_"]
            if any(api_key.startswith(suspicious) for suspicious in suspicious_keys):
                warnings.append("ODDS_API_KEY appears to be a placeholder")
        
        # Check optional but recommended variables
        recommended_vars = [
            "SENTRY_DSN",
            "REDIS_URL"
        ]
        
        for var in recommended_vars:
            if not os.getenv(var):
                warnings.append(f"Recommended environment variable not set: {var}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "is_railway": ProductionConfig.is_railway()
        }
    
    @staticmethod
    def get_cors_origins() -> List[str]:
        """Get appropriate CORS origins based on environment."""
        # Debug logging
        logger.info(f"CORS Debug - Environment: {os.getenv('ENVIRONMENT')}")
        logger.info(f"CORS Debug - Is Railway: {ProductionConfig.is_railway()}")
        logger.info(f"CORS Debug - Frontend URL: {os.getenv('FRONTEND_URL')}")
        logger.info(f"CORS Debug - CORS Origins: {os.getenv('CORS_ORIGINS')}")
        
        if ProductionConfig.is_production():
            origins = ProductionConfig.get_production_origins()
            
            # Allow wildcard CORS for Railway environments
            if ProductionConfig.is_railway():
                logger.warning("CORS: Railway environment detected, allowing all origins")
                return ["*"]
            
            # Add development origins only if explicitly allowed
            if os.getenv("ALLOW_DEV_ORIGINS_IN_PROD", "").lower() == "true":
                origins.extend(ProductionConfig.get_development_origins())
            
            # If no origins specified, allow the frontend URL if available
            if not origins:
                frontend_url = os.getenv("FRONTEND_URL", "").strip()
                if frontend_url:
                    origins = [frontend_url]
                else:
                    # Last resort - allow all origins but log warning
                    logger.warning("CORS: No origins specified, allowing all origins")
                    return ["*"]
            
            logger.info(f"CORS Debug - Final origins: {origins}")
            return origins
        
        # Development environment
        origins = ProductionConfig.get_development_origins()
        
        # Add production origins if specified
        if os.getenv("FRONTEND_URL"):
            origins.append(os.getenv("FRONTEND_URL"))
        
        return origins


@lru_cache
def get_production_config() -> ProductionConfig:
    """Get cached production config instance."""
    return ProductionConfig()


def validate_and_log_config() -> bool:
    """Validate production configuration and log results."""
    config = get_production_config()
    validation = config.validate_production_config()
    
    if validation["issues"]:
        for issue in validation["issues"]:
            logger.error(f"Production Config Issue: {issue}")
    
    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"Production Config Warning: {warning}")
    
    if validation["valid"]:
        logger.info("Production configuration validated successfully")
        logger.info(f"Environment: {validation['environment']}")
        logger.info(f"Railway: {validation['is_railway']}")
    else:
        logger.error("Production configuration validation failed")
    
    return validation["valid"]
