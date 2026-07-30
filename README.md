# payu-pyapi

Python API for PayU subscription data ( json with hash)  generation package. more features might be added in future.

please note that this is a work in progress and may not be production ready.

## About

payu-pyapi is a Python library that simplifies integration with PayU's payment gateway, specifically for subscription-based payments. It provides a clean, object-oriented interface to handle:

- Subscription json data generation with automatic hash calculation
- Transaction ID generation
- Subscription date management
- Support for both test and production environments

## Purpose

This library aims to:

- **Simplify PayU Integration**: Remove the complexity of manual hash generation and field preparation
- **Subscription Management**: Handle recurring billing setup with ease
- **Security**: Automate SHA512 hash generation for secure payment processing
- **Flexibility**: Support custom billing cycles, currencies, and subscription durations

## Use Cases

- **SaaS Platforms**: Implement recurring subscription payments for your software service
- **Membership Sites**: Handle monthly/yearly membership fees
- **Content Platforms**: Manage subscription-based content access
- **Service Businesses**: Automate recurring service payments
- **E-commerce**: Implement subscription-based product sales

## Features

- **Dual Environment Support**: Easy switching between test and production modes
- **Automatic Hash Generation**: SHA512 hash calculation for payment security
- **Subscription Management**: Built-in support for billing cycles (MONTHLY, WEEKLY, YEARLY)
- **Transaction ID Generation**: Unique, timestamped transaction identifiers
- **Flexible Configuration**: Customizable currency, duration, and billing intervals
- **Error Handling**: Custom exceptions for clear error reporting


## Installation

```bash
pip install payu-pyapi
```

## Quick Start

```python
from payu_pyapi import payu_test_man, payu_production_man

MERCHANT_KEY = "your_merchant_key"
SALT = "your_salt"

# For test environment
manager = payu_test_man(MERCHANT_KEY, SALT, amount=99)

# For production environment
manager = payu_production_man(MERCHANT_KEY, SALT, amount=99)
fields = {
            "firstname": "raju",
            "email": "raju@localhost.localhost",
            "phone": "0000000000",
            "surl": "https://localhost:3000/_/theme/payu_success.html",
            "furl": "https://localhost:3000/_/theme/payu_fail.html",
            "api_version": "7s",
            "si": "1",
      }
json_with_hash = manager.generate_subscription_link_data(fields)
print(json_with_hash)

```

## API Usage

### 1. Subscription Manager Setup

Initialize the subscription manager with your PayU credentials and subscription parameters:

```python
from payu_pyapi import payu_test_man

manager = payu_test_man(
    MERCHANT_KEY="your_key",
    SALT="your_salt",
    amount=99,                    # Billing amount
    productinfo="Premium Plan",   # Product name
    firstname="John",             # Customer first name
    email="john@example.com",     # Customer email
    currency="INR",               # Currency (default: INR)
    cycle="MONTHLY",              # Billing cycle: MONTHLY, WEEKLY, YEARLY
    duration=365                  # Subscription duration in days (default: 365)
)
```

### 2. Generate Subscription Link Data

Prepare the payment fields and generate the complete subscription link data with hash:

```python
fields = {
    "firstname": "John",
    "email": "john@example.com",
    "phone": "9876543210",
    "productinfo": "Premium Plan",
    "surl": "https://yourdomain.com/success",
    "furl": "https://yourdomain.com/failure",
    "api_version": "7",
    "si": "1"
}

subscription_data = manager.generate_subscription_link_data(fields)
print(subscription_data)
```

The returned data includes:
- All original fields
- Auto-generated transaction ID
- Subscription details (`si_details`)
- Payment hash for security

### 3. Create Subscription Dates

Manually create subscription start and end dates:

```python
from payu_pyapi import payu_test_man

manager = payu_test_man("your_key", "your_salt")

# Create dates for 1 year subscription
dates = manager.create_subscription_date(days=365)
print(dates)
# Output: {'paymentStartDate': '2026-07-29', 'paymentEndDate': '2027-07-29'}

# Create dates for custom duration
dates = manager.create_subscription_date(days=30)
print(dates)
# Output: {'paymentStartDate': '2026-07-29', 'paymentEndDate': '2026-08-28'}
```

### 4. Generate Subscription Details

Generate subscription information JSON:

```python
from payu_pyapi import payu_subscription

dates = payu_subscription.create_subscription_date(days=365)
si_details = payu_subscription.get_si_details(
    amount=99,
    date_obj=dates,
    currency="INR",
    cycle="MONTHLY"
)
print(si_details)
# Output: {
#     'billingAmount': '99',
#     'billingCurrency': 'INR',
#     'billingCycle': 'MONTHLY',
#     'billingInterval': 1,
#     'paymentStartDate': '2026-07-29',
#     'paymentEndDate': '2027-07-29'
# }
```

### 5. Generate Payment Hash

Generate a secure hash for payment verification:

```python
from payu_pyapi import payu_manager

fields = {
    'txnid': 'txn123',
    'amount': '100.00',
    'productinfo': 'Product Name',
    'firstname': 'John',
    'email': 'john@example.com',
    'si_details': {'billingAmount': '100', 'billingCurrency': 'INR', ...}
}

hash_value = payu_manager.generate_hash(
    fields,
    KEY="your_merchant_key",
    SALT="your_salt"
)
print(hash_value)
```

### 6. Generate Transaction ID

Generate a unique transaction ID:

```python
from payu_pyapi import payu

txn_id = payu.generate_transaction_id()
print(txn_id)
# Output: TXN-20260729023045-A1B2C3D4E5F6
```

### 7. Complete Example

```python
from payu_pyapi import payu_test_man

# Initialize manager
manager = payu_test_man(
    MERCHANT_KEY="your_key",
    SALT="your_salt",
    amount=99,
    productinfo="Premium Subscription",
    firstname="John",
    email="john@example.com",
    cycle="MONTHLY",
    duration=365
)

# Prepare payment fields
fields = {
    "phone": "9876543210",
    "surl": "https://yourdomain.com/success",
    "furl": "https://yourdomain.com/failure",
    "api_version": "7",
    "si": "1"
}

# Generate complete subscription data
subscription_data = manager.generate_subscription_link_data(fields)

# Use the data to create payment form or redirect
print(f"Transaction ID: {subscription_data['txnid']}")
print(f"Payment Hash: {subscription_data['hash']}")
print(f"Subscription Details: {subscription_data['si_details']}")
```

## Classes

### `payu_manager`
Base class for PayU API management.

**Methods:**
- `generate_hash(fields, KEY, SALT)`: Generate SHA512 hash for payment verification
- `generate_hash_self(fields)`: Generate hash and add to fields dictionary

### `payu_subscription`
Extended manager for subscription payments.

**Parameters:**
- `amount`: Billing amount (default: 1)
- `productinfo`: Product description
- `firstname`: Customer first name
- `email`: Customer email
- `currency`: Currency code (default: INR)
- `cycle`: Billing cycle - MONTHLY, WEEKLY, YEARLY (default: MONTHLY)
- `duration`: Subscription duration in days (default: 365)

**Methods:**
- `create_subscription_date(days)`: Create subscription start/end dates
- `get_si_details(amount, date_obj, currency, cycle)`: Generate subscription details JSON
- `generate_subscription_link_data(fields)`: Generate complete subscription data with hash

### `payu_test_man`
Test environment manager (uses test.payu.in)

### `payu_production_man`
Production environment manager (uses secure.payu.in)

### `Error`
Custom exception for PayU API errors

## Helper Functions

### `generate_transaction_id()`
Generate a unique transaction ID in format: `TXN-YYYYMMDDHHMMSS-RANDOM`

### `get_test_data_json()`
Get sample payment fields for testing (includes localhost URLs)

## Environment Variables

For security, you can store credentials in environment variables:

```bash
export PAYU_KEY="your_merchant_key"
export PAYU_SALT="your_salt"
```

Then use in your code:

```python
import os
from payu_pyapi import payu_test_man

manager = payu_test_man(
    MERCHANT_KEY=os.getenv("PAYU_KEY"),
    SALT=os.getenv("PAYU_SALT")
)
```

## Error Handling

```python
from payu_pyapi import payu_test_man, Error

try:
    manager = payu_test_man("", "")  # Invalid credentials
except Error as e:
    print(f"PayU Error: {e}")
```

## License

GNU Affero General Public License v3.0 (AGPL-3.0)
