"""Utilities Package

This package contains helper functions and utilities for the mAIgic_core
components, including intent helpers, time utilities, and other shared functions.
"""

from .intent_helpers import (
    create_intent_from_type,
    validate_intent_data,
    intent_to_dict,
    intent_from_dict,
)
from .time_helpers import (
    time_slot_from_string,
    time_slot_to_string,
    parse_natural_time,
    format_duration,
    is_time_slot_available,
)
from .validation import (
    validate_user_context,
    validate_assistant_config,
    sanitize_user_input,
)

__all__ = [
    # Intent helpers
    "create_intent_from_type",
    "validate_intent_data",
    "intent_to_dict",
    "intent_from_dict",
    
    # Time helpers
    "time_slot_from_string",
    "time_slot_to_string",
    "parse_natural_time",
    "format_duration",
    "is_time_slot_available",
    
    # Validation
    "validate_user_context",
    "validate_assistant_config",
    "sanitize_user_input",
] 