"""
Basic health check tests to verify the test infrastructure works.
"""
import pytest


def test_health_check_basic():
    """Verify basic test infrastructure is working."""
    assert True


def test_imports():
    """Verify core modules can be imported."""
    from app.core.config import Settings
    from app.models.sport import Sport
    from app.models.game import Game
    from app.models.player import Player
    
    # Verify classes exist
    assert Settings is not None
    assert Sport is not None
    assert Game is not None
    assert Player is not None


def test_settings_defaults():
    """Test that Settings can be instantiated with defaults."""
    import os
    # Set minimal required env vars for testing
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    
    from app.core.config import Settings
    settings = Settings()
    
    assert settings is not None
    assert hasattr(settings, 'database_url')


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_scheduler_defaults(self):
        """Test scheduler configuration defaults."""
        import os
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        
        from app.core.config import Settings
        settings = Settings()
        
        # Scheduler should have reasonable defaults
        assert hasattr(settings, 'scheduler_enabled')
