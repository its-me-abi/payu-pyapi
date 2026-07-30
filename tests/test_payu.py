import pytest
from datetime import datetime, timedelta
from payu_pyapi.payu import (
    payu_manager,
    payu_test_man,
    payu_production_man,
    Error,
    PAYU_TEST_URL,
    PAYU_SECURE_URL
)


class TestError:
    """Test the custom Error exception."""
    
    def test_error_is_exception(self):
        """Verify Error is an Exception subclass."""
        assert issubclass(Error, Exception)
    
    def test_error_can_be_raised(self):
        """Verify Error can be raised and caught."""
        with pytest.raises(Error):
            raise Error("Test error message")


class TestPayuManagerInitialization:
    """Test payu_manager class initialization."""
    
    def test_initialization_with_valid_params(self):
        """Test successful initialization with valid key and salt."""
        manager = payu_manager("test_key", "test_salt")
        assert manager.MERCHANT_KEY == "test_key"
        assert manager.SALT == "test_salt"
        assert manager.PAYU_URL == PAYU_TEST_URL
    
    def test_initialization_with_custom_url(self):
        """Test initialization with custom PAYU_URL."""
        custom_url = "https://custom.url"
        manager = payu_manager("test_key", "test_salt", custom_url)
        assert manager.PAYU_URL == custom_url
    
    def test_initialization_with_empty_key_raises_error(self):
        """Test that empty key raises Error."""
        with pytest.raises(Error, match="you should provide key and salt"):
            payu_manager("", "test_salt")
    
    def test_initialization_with_empty_salt_raises_error(self):
        """Test that empty salt raises Error."""
        with pytest.raises(Error, match="you should provide key and salt"):
            payu_manager("test_key", "")
    
    def test_initialization_with_none_key_raises_error(self):
        """Test that None key raises Error."""
        with pytest.raises(Error, match="you should provide key and salt"):
            payu_manager(None, "test_salt")
    
    def test_initialization_with_none_salt_raises_error(self):
        """Test that None salt raises Error."""
        with pytest.raises(Error, match="you should provide key and salt"):
            payu_manager("test_key", None)
    
    def test_initialization_with_non_string_key_raises_error(self):
        """Test that non-string key raises Error."""
        with pytest.raises(Error, match="key and salt should be strings"):
            payu_manager(123, "test_salt")
    
    def test_initialization_with_non_string_salt_raises_error(self):
        """Test that non-string salt raises Error."""
        with pytest.raises(Error, match="key and salt should be strings"):
            payu_manager("test_key", 123)


class TestCreateSubscriptionDate:
    """Test the create_subscription_date static method."""
    
    def test_default_days(self):
        """Test subscription date creation with default days (365*30)."""
        result = payu_manager.create_subscription_date()
        assert "paymentStartDate" in result
        assert "paymentEndDate" in result
        assert isinstance(result["paymentStartDate"], str)
        assert isinstance(result["paymentEndDate"], str)
    
    def test_custom_days(self):
        """Test subscription date creation with custom days."""
        result = payu_manager.create_subscription_date(days=365)
        start_date = datetime.strptime(result["paymentStartDate"], "%Y-%m-%d")
        end_date = datetime.strptime(result["paymentEndDate"], "%Y-%m-%d")
        expected_end = start_date + timedelta(days=365)
        assert (end_date - expected_end).total_seconds() < 1
    
    def test_date_format(self):
        """Test that dates are in correct format (YYYY-MM-DD)."""
        result = payu_manager.create_subscription_date(days=30)
        assert len(result["paymentStartDate"]) == 10
        assert len(result["paymentEndDate"]) == 10
        # Verify format by parsing
        datetime.strptime(result["paymentStartDate"], "%Y-%m-%d")
        datetime.strptime(result["paymentEndDate"], "%Y-%m-%d")


class TestGenerateHash:
    """Test the generate_hash static method."""
    
    def test_generate_hash_with_all_fields(self):
        """Test hash generation with all required fields."""
        fields = {
            "txnid": "test_txn123",
            "amount": "100.00",
            "productinfo": "test_product",
            "firstname": "John",
            "email": "john@example.com",
            "udf1": "value1",
            "udf2": "value2",
            "udf3": "value3",
            "udf4": "value4",
            "udf5": "value5",
            "si_details": "test_si_details"
        }
        key = "test_key"
        salt = "test_salt"
        
        result = payu_manager.generate_hash(fields, key, salt)
        assert isinstance(result, str)
        assert len(result) == 128  # SHA512 produces 128 hex characters
    
    def test_generate_hash_without_udf_fields(self):
        """Test hash generation without optional udf fields."""
        fields = {
            "txnid": "test_txn123",
            "amount": "100.00",
            "productinfo": "test_product",
            "firstname": "John",
            "email": "john@example.com",
            "si_details": "test_si_details"
        }
        key = "test_key"
        salt = "test_salt"
        
        result = payu_manager.generate_hash(fields, key, salt)
        assert isinstance(result, str)
        assert len(result) == 128
    
    def test_generate_hash_consistency(self):
        """Test that hash generation is consistent for same inputs."""
        fields = {
            "txnid": "test_txn123",
            "amount": "100.00",
            "productinfo": "test_product",
            "firstname": "John",
            "email": "john@example.com",
            "si_details": "test_si_details"
        }
        key = "test_key"
        salt = "test_salt"
        
        hash1 = payu_manager.generate_hash(fields, key, salt)
        hash2 = payu_manager.generate_hash(fields, key, salt)
        assert hash1 == hash2
    
    def test_generate_hash_different_inputs(self):
        """Test that different inputs produce different hashes."""
        fields1 = {
            "txnid": "txn1",
            "amount": "100.00",
            "productinfo": "product",
            "firstname": "John",
            "email": "john@example.com",
            "si_details": "si_details"
        }
        fields2 = {
            "txnid": "txn2",
            "amount": "100.00",
            "productinfo": "product",
            "firstname": "John",
            "email": "john@example.com",
            "si_details": "si_details"
        }
        key = "test_key"
        salt = "test_salt"
        
        hash1 = payu_manager.generate_hash(fields1, key, salt)
        hash2 = payu_manager.generate_hash(fields2, key, salt)
        assert hash1 != hash2


class TestGenerateHashSelf:
    """Test the __generate_hash_self method."""
    
    def test_generate_hash_self_valid_fields(self):
        """Test __generate_hash_self with valid fields."""
        manager = payu_manager("test_key", "test_salt")
        fields = {
            "txnid": "test_txn123",
            "amount": "100.00",
            "productinfo": "test_product",
            "firstname": "John",
            "email": "john@example.com",
            "si_details": "test_si_details"
        }
        
        result = manager._payu_manager__generate_hash_self(fields)
        assert isinstance(result, str)
        assert len(result) == 128
    
    def test_generate_hash_self_missing_required_field(self):
        """Test __generate_hash_self with missing required field raises Error."""
        manager = payu_manager("test_key", "test_salt")
        fields = {
            "txnid": "test_txn123",
            "amount": "100.00",
            "productinfo": "test_product",
            "firstname": "John",
            # Missing email
            "si_details": "test_si_details"
        }
        
        with pytest.raises(Error, match="required keys of payu subscription web api not provided"):
            manager._payu_manager__generate_hash_self(fields)
    
    def test_generate_hash_self_uses_instance_credentials(self):
        """Test that __generate_hash_self uses instance key and salt."""
        manager = payu_manager("instance_key", "instance_salt")
        fields = {
            "txnid": "test_txn123",
            "amount": "100.00",
            "productinfo": "test_product",
            "firstname": "John",
            "email": "john@example.com",
            "si_details": "test_si_details"
        }
        
        result = manager._payu_manager__generate_hash_self(fields)
        # Compare with static method using same credentials
        static_result = payu_manager.generate_hash(fields, "instance_key", "instance_salt")
        assert result == static_result


class TestPayuTestMan:
    """Test payu_test_man subclass."""
    
    def test_initialization_uses_test_url(self):
        """Test that payu_test_man defaults to PAYU_TEST_URL."""
        test_manager = payu_test_man("test_key", "test_salt")
        assert test_manager.PAYU_URL == PAYU_TEST_URL
    
    def test_initialization_with_custom_url_overrides_default(self):
        """Test that custom URL overrides default in payu_test_man."""
        custom_url = "https://custom.url"
        test_manager = payu_test_man("test_key", "test_salt", PAYU_URL=custom_url)
        assert test_manager.PAYU_URL == custom_url
    
    def test_inheritance_from_payu_manager(self):
        """Test that payu_test_man inherits from payu_manager."""
        assert isinstance(payu_test_man("test_key", "test_salt"), payu_manager)


class TestPayuProductionMan:
    """Test payu_production_man subclass."""
    
    def test_initialization_uses_secure_url(self):
        """Test that payu_production_man defaults to PAYU_SECURE_URL."""
        prod_manager = payu_production_man("test_key", "test_salt")
        assert prod_manager.PAYU_URL == PAYU_SECURE_URL
    
    def test_initialization_with_custom_url_overrides_default(self):
        """Test that custom URL overrides default in payu_production_man."""
        custom_url = "https://custom.url"
        prod_manager = payu_production_man("test_key", "test_salt", PAYU_URL=custom_url)
        assert prod_manager.PAYU_URL == custom_url
    
    def test_inheritance_from_payu_manager(self):
        """Test that payu_production_man inherits from payu_manager."""
        assert isinstance(payu_production_man("test_key", "test_salt"), payu_manager)


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow_test_environment(self):
        """Test complete workflow in test environment."""
        manager = payu_test_man("test_key", "test_salt")
        
        # Create subscription dates
        dates = manager.create_subscription_date(days=365)
        assert "paymentStartDate" in dates
        assert "paymentEndDate" in dates
        
        # Generate hash
        fields = {
            "txnid": "txn123",
            "amount": "500.00",
            "productinfo": "premium_subscription",
            "firstname": "Alice",
            "email": "alice@example.com",
            "si_details": "subscription_details"
        }
        hash_value = manager._payu_manager__generate_hash_self(fields)
        assert hash_value
        assert len(hash_value) == 128
    
    def test_full_workflow_production_environment(self):
        """Test complete workflow in production environment."""
        manager = payu_production_man("prod_key", "prod_salt")
        
        # Create subscription dates
        dates = manager.create_subscription_date(days=30)
        assert "paymentStartDate" in dates
        assert "paymentEndDate" in dates
        
        # Generate hash
        fields = {
            "txnid": "txn456",
            "amount": "99.99",
            "productinfo": "basic_plan",
            "firstname": "Bob",
            "email": "bob@example.com",
            "si_details": "subscription_details"
        }
        hash_value = manager._payu_manager__generate_hash_self(fields)
        assert hash_value
        assert len(hash_value) == 128
