"""
Dummy data sent from Plaid used for testing.
"""

# Accounts
ACCOUNTS = [
    {
        "account_id": "blgvvBlXw3cq5GMPwqB6s6q4dLKB9WcVqGDGo",
        "balances": {
            "available": 100,
            "current": 110,
            "iso_currency_code": "USD",
            "limit": 10,
            "unofficial_currency_code": "USD",
        },
        "mask": "0000",
        "name": "Plaid Checking",
        "official_name": "Plaid Gold Standard 0% Interest Checking",
        "persistent_account_id": "8cfb8beb89b774ee43b090625f0d61d0814322b43bff984eaf60386e",
        "subtype": "checking",
        "type": "depository",
    },
    {
        "account_id": "6PdjjRP6LmugpBy5NgQvUqpRXMWxzktg3rwrk",
        "balances": {
            "available": None,
            "current": 23631.9805,
            "iso_currency_code": "USD",
            "limit": None,
            "unofficial_currency_code": None,
        },
        "mask": "6666",
        "name": "Plaid 401k",
        "official_name": None,
        "subtype": "401k",
        "type": "investment",
    },
    {
        "account_id": "XMBvvyMGQ1UoLbKByoMqH3nXMj84ALSdE5B58",
        "balances": {
            "available": None,
            "current": 65262,
            "iso_currency_code": "USD",
            "limit": None,
            "unofficial_currency_code": None,
        },
        "mask": "7777",
        "name": "Plaid Student Loan",
        "official_name": None,
        "subtype": "student",
        "type": "loan",
    },
]
ACCOUNTS_RESPONSE = {
    "accounts": ACCOUNTS,
    "item": {
        "available_products": [
            "balance",
            "identity",
            "payment_initiation",
            "transactions",
        ],
        "billed_products": ["assets", "auth"],
        "consent_expiration_time": None,
        "error": None,
        "institution_id": "ins_117650",
        "item_id": "DWVAAPWq4RHGlEaNyGKRTAnPLaEmo8Cvq7na6",
        "update_type": "background",
        "webhook": "https://www.genericwebhookurl.com/webhook",
    },
    "request_id": "bkVE1BHWMAZ9Rnr",
}

# Transactions
TRANSACTIONS_ADDED = [
    {
        "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
        "account_owner": None,
        "amount": 72.1,
        "iso_currency_code": "USD",
        "unofficial_currency_code": None,
        "category": ["Shops", "Supermarkets and Groceries"],
        "category_id": "19046000",
        "check_number": None,
        "counterparties": [
            {
                "name": "Walmart",
                "type": "merchant",
                "logo_url": "https://plaid-merchant-logos.plaid.com/walmart_1100.png",
                "website": "walmart.com",
                "entity_id": "O5W5j4dN9OR3E6ypQmjdkWZZRoXEzVMz2ByWM",
                "confidence_level": "VERY_HIGH",
            }
        ],
        "date": "2023-09-24",
        "datetime": "2023-09-24T11:01:01Z",
        "authorized_date": "2023-09-22",
        "authorized_datetime": "2023-09-22T10:34:50Z",
        "location": {
            "address": "13425 Community Rd",
            "city": "Poway",
            "region": "CA",
            "postal_code": "92064",
            "country": "US",
            "lat": 32.959068,
            "lon": -117.037666,
            "store_number": "1700",
        },
        "name": "PURCHASE WM SUPERCENTER #1700",
        "merchant_name": "Walmart",
        "merchant_entity_id": "O5W5j4dN9OR3E6ypQmjdkWZZRoXEzVMz2ByWM",
        "logo_url": "https://plaid-merchant-logos.plaid.com/walmart_1100.png",
        "website": "walmart.com",
        "payment_meta": {
            "by_order_of": None,
            "payee": None,
            "payer": None,
            "payment_method": None,
            "payment_processor": None,
            "ppd_id": None,
            "reason": None,
            "reference_number": None,
        },
        "payment_channel": "in store",
        "pending": False,
        "pending_transaction_id": "no86Eox18VHMvaOVL7gPUM9ap3aR1LsAVZ5nc",
        "personal_finance_category": {
            "primary": "GENERAL_MERCHANDISE",
            "detailed": "GENERAL_MERCHANDISE_SUPERSTORES",
            "confidence_level": "VERY_HIGH",
        },
        "personal_finance_category_icon_url": "https://plaid-category-icons.plaid.com/PFC_GENERAL_MERCHANDISE.png",
        "transaction_id": "lPNjeW1nR6CDn5okmGQ6hEpMo4lLNoSrzqDje",
        "transaction_code": None,
        "transaction_type": "place",
    }
]
TRANSACTIONS_MODIFIED = [
    {
        "account_id": "BxBXxLj1m4HMXBm9WZZmCWVbPjX16EHwv99vp",
        "account_owner": None,
        "amount": 28.34,
        "iso_currency_code": "USD",
        "unofficial_currency_code": None,
        "category": ["Food and Drink", "Restaurants", "Fast Food"],
        "category_id": "13005032",
        "check_number": None,
        "counterparties": [
            {
                "name": "DoorDash",
                "type": "marketplace",
                "logo_url": "https://plaid-counterparty-logos.plaid.com/doordash_1.png",
                "website": "doordash.com",
                "entity_id": "YNRJg5o2djJLv52nBA1Yn1KpL858egYVo4dpm",
                "confidence_level": "HIGH",
            },
            {
                "name": "Burger King",
                "type": "merchant",
                "logo_url": "https://plaid-merchant-logos.plaid.com/burger_king_155.png",
                "website": "burgerking.com",
                "entity_id": "mVrw538wamwdm22mK8jqpp7qd5br0eeV9o4a1",
                "confidence_level": "VERY_HIGH",
            },
        ],
        "date": "2023-09-28",
        "datetime": "2023-09-28T15:10:09Z",
        "authorized_date": "2023-09-27",
        "authorized_datetime": "2023-09-27T08:01:58Z",
        "location": {
            "address": None,
            "city": None,
            "region": None,
            "postal_code": None,
            "country": None,
            "lat": None,
            "lon": None,
            "store_number": None,
        },
        "name": "Dd Doordash Burgerkin",
        "merchant_name": "Burger King",
        "merchant_entity_id": "mVrw538wamwdm22mK8jqpp7qd5br0eeV9o4a1",
        "logo_url": "https://plaid-merchant-logos.plaid.com/burger_king_155.png",
        "website": "burgerking.com",
        "payment_meta": {
            "by_order_of": None,
            "payee": None,
            "payer": None,
            "payment_method": None,
            "payment_processor": None,
            "ppd_id": None,
            "reason": None,
            "reference_number": None,
        },
        "payment_channel": "online",
        "pending": True,
        "pending_transaction_id": None,
        "personal_finance_category": {
            "primary": "FOOD_AND_DRINK",
            "detailed": "FOOD_AND_DRINK_FAST_FOOD",
            "confidence_level": "VERY_HIGH",
        },
        "personal_finance_category_icon_url": "https://plaid-category-icons.plaid.com/PFC_FOOD_AND_DRINK.png",
        "transaction_id": "yhnUVvtcGGcCKU0bcz8PDQr5ZUxUXebUvbKC0",
        "transaction_code": None,
        "transaction_type": "digital",
    }
]
TRANSACTIONS_REMOVED = [{"transaction_id": "CmdQTNgems8BT1B7ibkoUXVPyAeehT3Tmzk0l"}]
TRANSACTIONS_CURSOR = (
    "tVUUL15lYQN5rBnfDIc1I8xudpGdIlw9nsgeXWvhOfkECvUeR663i3Dt1uf/94S8ASkitgLcIiOSqNwzzp+bh89kirazha5vuZHBb2ZA5NtCDkkV"
)
TRANSACTIONS_SYNC_RESPONSE = {
    "added": TRANSACTIONS_ADDED,
    "modified": TRANSACTIONS_MODIFIED,
    "removed": TRANSACTIONS_REMOVED,
    "next_cursor": TRANSACTIONS_CURSOR,
    "has_more": False,
    "request_id": "Wvhy9PZHQLV8njG",
}
