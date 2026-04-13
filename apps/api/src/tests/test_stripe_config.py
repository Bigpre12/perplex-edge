import os
import pytest
from core.config import Settings

def test_stripe_config_loading():
    # Mock environment variables for testing
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_mock"
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_mock"
    os.environ["STRIPE_PRO_MONTHLY_PRICE_ID"] = "price_pro_m"
    os.environ["STRIPE_PRO_ANNUAL_PRICE_ID"] = "price_pro_a"
    os.environ["STRIPE_ELITE_MONTHLY_PRICE_ID"] = "price_elite_m"
    os.environ["STRIPE_ELITE_ANNUAL_PRICE_ID"] = "price_elite_a"
    
    settings = Settings()
    
    assert settings.STRIPE_SECRET_KEY == "sk_test_mock"
    assert settings.STRIPE_WEBHOOK_SECRET == "whsec_mock"
    assert settings.STRIPE_PRO_MONTHLY_PRICE_ID == "price_pro_m"
    assert settings.STRIPE_PRO_ANNUAL_PRICE_ID == "price_pro_a"
    assert settings.STRIPE_ELITE_MONTHLY_PRICE_ID == "price_elite_m"
    assert settings.STRIPE_ELITE_ANNUAL_PRICE_ID == "price_elite_a"
    
    # Check aliases
    assert settings.STRIPE_PRO_PRICE_ID == "price_pro_m"
    assert settings.STRIPE_ELITE_PRICE_ID == "price_elite_m"

if __name__ == "__main__":
    test_stripe_config_loading()
    print("Stripe configuration test passed!")
