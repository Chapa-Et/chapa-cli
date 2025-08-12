"""
Validation utilities for Chapa CLI.
"""

import click
from decimal import Decimal
from enum import Enum
from typing import Optional

import validators
import phonenumbers
from phonenumbers import NumberParseException
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, Field, field_validator, model_validator


class AccountType(str, Enum):
    """Chapa account types with their transaction limits."""
    INDIVIDUAL_UNAPPROVED = "individual_unapproved"
    INDIVIDUAL_APPROVED = "individual_approved" 
    BUSINESS_UNAPPROVED = "business_unapproved"
    BUSINESS_APPROVED = "business_approved"
    NGO_UNAPPROVED = "ngo_unapproved"
    NGO_APPROVED = "ngo_approved"


class ChapaLimits:
    """ Chapa transaction limits in ETB."""
    
    LIMITS = {
        AccountType.INDIVIDUAL_UNAPPROVED: {
            "max_transaction": Decimal("50000"),
            "daily_cumulative": Decimal("200000")
        },
        AccountType.INDIVIDUAL_APPROVED: {
            "max_transaction": Decimal("200000"),
            "daily_cumulative": Decimal("500000")
        },
        AccountType.BUSINESS_UNAPPROVED: {
            "max_transaction": Decimal("200000"),
            "daily_cumulative": Decimal("1000000")
        },
        AccountType.BUSINESS_APPROVED: {
            "max_transaction": Decimal("500000"),
            "daily_cumulative": None  # Not provided
        },
        AccountType.NGO_UNAPPROVED: {
            "max_transaction": Decimal("50000"),
            "daily_cumulative": Decimal("200000")
        },
        AccountType.NGO_APPROVED: {
            "max_transaction": Decimal("500000"),
            "daily_cumulative": Decimal("1000000")
        }
    }

    @classmethod
    def get_limits(cls, account_type: AccountType) -> dict:
        """Get transaction limits for account type."""
        return cls.LIMITS.get(account_type, cls.LIMITS[AccountType.INDIVIDUAL_UNAPPROVED])


class TransactionAmount(BaseModel):
    """Validate transaction amounts with Chapa limits."""
    
    amount: Decimal = Field(gt=0, description="Amount must be positive")
    currency: str = Field(pattern=r"^[A-Z]{3}$", description="Currency must be 3-letter ISO code")
    account_type: AccountType = Field(default=AccountType.INDIVIDUAL_UNAPPROVED)
    
    @model_validator(mode='after')
    def validate_amount_limits(self):
        """Validate amount against Chapa limits using model validator."""
        limits = ChapaLimits.get_limits(self.account_type)
        
        max_transaction = limits['max_transaction']
        if self.amount > max_transaction:
            raise ValueError(
                f"Amount {self.amount} ETB exceeds maximum transaction limit of {max_transaction} ETB "
                f"for {self.account_type.value} accounts"
            )
        return self
    
    @field_validator('currency')
    @classmethod
    def validate_currency_chapa(cls, v):
        """Validate currency is supported by Chapa."""
        supported_currencies = {"ETB", "USD"}  
        if v not in supported_currencies:
            raise ValueError(f"Currency {v} not supported. Supported: {supported_currencies}")
        return v


def validate_email_input(email: str) -> str:
    """Validate email using email validator."""
    if not email:
        raise click.BadParameter("Email is required")
    
    try:
        valid = validate_email(email)
        return valid.normalized  # Use .normalized instead of deprecated .email
    except EmailNotValidError as e:
        raise click.BadParameter(f"Invalid email address: {str(e)}")


def validate_phone_input(phone: str, region: str = "ET") -> str:
    """Validate phone number."""
    if not phone:
        raise click.BadParameter("Phone number is required")
    
    try:
        parsed = phonenumbers.parse(phone, region)
        if not phonenumbers.is_valid_number(parsed):
            raise click.BadParameter(f"Invalid phone number: {phone}")
        
        # Return in E164 format for API consistency
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException as e:
        raise click.BadParameter(f"Invalid phone number format: {str(e)}")


def validate_amount_input(
    amount: str, 
    currency: str = "ETB", 
    account_type: AccountType = AccountType.INDIVIDUAL_UNAPPROVED
) -> Decimal:
    """Validate transaction amount with Chapa limits."""
    try:
        amount_decimal = Decimal(amount)
    except (ValueError, TypeError):
        raise click.BadParameter(f"Invalid amount format: {amount}")
    
    try:
        validated = TransactionAmount(
            amount=amount_decimal,
            currency=currency.upper(),
            account_type=account_type
        )
        return validated.amount
    except ValueError as e:
        raise click.BadParameter(str(e))


def validate_url_input(url: str, require_https: bool = True) -> str:
    """Validate URL format with optional HTTPS requirement."""
    if not url:
        raise click.BadParameter("URL is required")
    
    if not validators.url(url):
        raise click.BadParameter(f"Invalid URL format: {url}")
    
    if require_https and not url.startswith('https://'):
        raise click.BadParameter("HTTPS URL required for security")
    
    return url


def validate_tx_ref(tx_ref: str) -> str:
    """Validate transaction reference format."""
    if not tx_ref:
        raise click.BadParameter("Transaction reference is required")
    
    if len(tx_ref) < 3:
        raise click.BadParameter("Transaction reference must be at least 3 characters")
    
    if len(tx_ref) > 50:
        raise click.BadParameter("Transaction reference must be less than 50 characters")
    
    # Basic alphanumeric validation
    if not tx_ref.replace('-', '').replace('_', '').isalnum():
        raise click.BadParameter("Transaction reference can only contain letters, numbers, hyphens, and underscores")
    
    return tx_ref


def get_account_type_from_user() -> AccountType:
    """Get account type from user for limit validation."""
    # Default to individual unapproved
    return AccountType.INDIVIDUAL_UNAPPROVED
