"""
Production AI Redactor System

A configurable LLM-based document redaction system that supports:
- Multiple redaction techniques (mask with ***, substitute with equivalent values)
- Configurable data types to redact
- Specific individuals/entities targeting
- Variable sophistication levels for comprehensive redaction
- Two-phase processing: masking before substitution
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import requests

import config


class RedactionTechnique(Enum):
    """Redaction technique options"""
    MASK = "mask"           # Replace with ***
    SUBSTITUTE = "substitute"  # Replace with equivalent values
    BOTH = "both"           # Apply mask first, then substitute remaining


class SophisticationLevel(Enum):
    """How comprehensive the redaction should be"""
    MINIMAL = "minimal"     # Only explicit PII (SSN, phone, email, full names)
    STANDARD = "standard"   # + Addresses, dates of birth, account numbers
    COMPREHENSIVE = "comprehensive"  # + Nicknames, locations, employers, relationships
    PARANOID = "paranoid"   # + Any info that could lead to deduction/re-identification


@dataclass
class DataTypeConfig:
    """Configuration for which data types to redact"""
    names: bool = True
    ssn: bool = True
    phone_numbers: bool = True
    email_addresses: bool = True
    physical_addresses: bool = True
    dates_of_birth: bool = True
    financial_accounts: bool = True
    medical_info: bool = True
    biometric_data: bool = True
    ip_addresses: bool = True
    usernames: bool = True
    passwords: bool = True
    
    # Extended types (enabled at higher sophistication levels)
    nicknames: bool = False
    locations: bool = False
    employers: bool = False
    relationships: bool = False
    educational_history: bool = False
    physical_descriptions: bool = False
    vehicle_info: bool = False
    travel_history: bool = False
    
    @classmethod
    def for_level(cls, level: SophisticationLevel) -> "DataTypeConfig":
        """Create a config appropriate for the given sophistication level"""
        cfg = cls()
        
        if level == SophisticationLevel.MINIMAL:
            cfg.physical_addresses = False
            cfg.dates_of_birth = False
            cfg.financial_accounts = False
            cfg.medical_info = False
            cfg.biometric_data = False
            cfg.ip_addresses = False
            cfg.usernames = False
            
        elif level == SophisticationLevel.COMPREHENSIVE:
            cfg.nicknames = True
            cfg.locations = True
            cfg.employers = True
            cfg.relationships = True
            
        elif level == SophisticationLevel.PARANOID:
            cfg.nicknames = True
            cfg.locations = True
            cfg.employers = True
            cfg.relationships = True
            cfg.educational_history = True
            cfg.physical_descriptions = True
            cfg.vehicle_info = True
            cfg.travel_history = True
            
        return cfg


@dataclass
class RedactorConfig:
    """Main configuration for the redactor"""
    technique: RedactionTechnique = RedactionTechnique.BOTH
    sophistication: SophisticationLevel = SophisticationLevel.STANDARD
    data_types: Optional[DataTypeConfig] = None
    
    # Specific individuals to always redact (by name)
    target_individuals: list = field(default_factory=list)
    
    # Custom patterns to always redact (regex patterns)
    custom_patterns: list = field(default_factory=list)
    
    # Mask character for MASK technique
    mask_char: str = "*"
    mask_length: int = 3  # Number of mask characters (e.g., ***)
    
    # For SUBSTITUTE technique - maintain consistency
    maintain_gender: bool = True
    maintain_ethnicity_hints: bool = False
    maintain_name_length: bool = False
    
    # LLM settings
    model: Optional[str] = None  # Override default model
    temperature: float = 0.1    # Low temp for consistency
    
    def __post_init__(self):
        if self.data_types is None:
            self.data_types = DataTypeConfig.for_level(self.sophistication)


class Redactor:
    """Production AI-powered document redactor"""
    
    def __init__(self, cfg: Optional[RedactorConfig] = None):
        self.config = cfg or RedactorConfig()
        self.substitution_map = {}  # Track substitutions for consistency
    
    def redact(self, document: str) -> str:
        """
        Redact sensitive information from a document.
        
        If technique is BOTH, applies mask redaction first (for data that
        should be completely hidden), then substitution (for data that
        needs realistic replacements).
        """
        if self.config.technique == RedactionTechnique.MASK:
            return self._redact_with_mask(document)
        elif self.config.technique == RedactionTechnique.SUBSTITUTE:
            return self._redact_with_substitution(document)
        else:  # BOTH - mask first, then substitute
            masked = self._redact_with_mask(document, partial=True)
            return self._redact_with_substitution(masked)
    
    def _redact_with_mask(self, document: str, partial: bool = False) -> str:
        """Apply mask-style redaction (replacing with ***)"""
        mask = self.config.mask_char * self.config.mask_length
        
        prompt = self._build_mask_prompt(document, mask, partial)
        system_msg = self._build_mask_system_message(partial)
        
        return self._call_llm(prompt, system_msg)
    
    def _redact_with_substitution(self, document: str) -> str:
        """Apply substitution-style redaction (replacing with equivalent values)"""
        prompt = self._build_substitution_prompt(document)
        system_msg = self._build_substitution_system_message()
        
        return self._call_llm(prompt, system_msg)
    
    def _build_mask_prompt(self, document: str, mask: str, partial: bool) -> str:
        """Build the prompt for mask-style redaction"""
        data_types = self._get_mask_data_types_description(partial)
        individuals = self._get_individuals_description()
        patterns = self._get_patterns_description()
        
        prompt = f"""Redact the following document by replacing sensitive information with "{mask}".

DOCUMENT TO REDACT:
---
{document}
---

DATA TYPES TO REDACT WITH "{mask}":
{data_types}

{individuals}
{patterns}

INSTRUCTIONS:
1. Replace each instance of the specified data types with exactly "{mask}"
2. Preserve all other text exactly as-is, including formatting and whitespace
3. Do NOT add explanations or commentary
4. Return ONLY the redacted document

REDACTED DOCUMENT:"""
        
        return prompt
    
    def _build_substitution_prompt(self, document: str) -> str:
        """Build the prompt for substitution-style redaction"""
        data_types = self._get_substitution_data_types_description()
        individuals = self._get_individuals_description()
        consistency_rules = self._get_consistency_rules()
        
        prompt = f"""Redact the following document by replacing sensitive information with realistic substitute values.

DOCUMENT TO REDACT:
---
{document}
---

DATA TYPES TO SUBSTITUTE:
{data_types}

{individuals}

SUBSTITUTION RULES:
{consistency_rules}
- Use realistic, plausible replacement values
- Maintain consistency: if "John Smith" becomes "Robert Johnson", use "Robert Johnson" throughout
- Preserve the document's readability and natural flow
- Do NOT add explanations or commentary
- Do NOT replace text already marked with "***" - leave those as-is
- Return ONLY the redacted document

REDACTED DOCUMENT:"""
        
        return prompt
    
    def _build_mask_system_message(self, partial: bool) -> str:
        """System message for mask redaction"""
        level_desc = {
            SophisticationLevel.MINIMAL: "basic PII only",
            SophisticationLevel.STANDARD: "standard PII and sensitive data",
            SophisticationLevel.COMPREHENSIVE: "comprehensive sensitive data including indirect identifiers",
            SophisticationLevel.PARANOID: "maximum privacy - anything that could lead to re-identification"
        }
        
        scope = level_desc[self.config.sophistication]
        phase = "first phase (masking critical data)" if partial else "complete masking"
        
        return f"""You are a privacy protection specialist performing document redaction.
Your task is {phase} redaction at the {self.config.sophistication.value} level ({scope}).
Replace sensitive data with the mask character exactly as instructed.
Preserve document structure and non-sensitive content exactly.
Return only the redacted document with no additional text."""
    
    def _build_substitution_system_message(self) -> str:
        """System message for substitution redaction"""
        level_desc = {
            SophisticationLevel.MINIMAL: "basic PII",
            SophisticationLevel.STANDARD: "standard PII and sensitive data",
            SophisticationLevel.COMPREHENSIVE: "comprehensive data including nicknames, locations, and indirect identifiers",
            SophisticationLevel.PARANOID: "maximum privacy - replacing anything that could enable re-identification"
        }
        
        scope = level_desc[self.config.sophistication]
        
        return f"""You are a privacy protection specialist performing document redaction via substitution.
Your task is replacing {scope} with realistic equivalent values.
For names, use plausible alternative names that maintain readability.
For locations, use different but similar locations (same type: city->city, state->state).
For numbers, generate realistic alternatives of the same format.
Maintain consistency: same original value = same replacement throughout.
Skip any text already marked with "***" - those are intentionally masked.
Return only the redacted document with no additional text."""
    
    def _get_mask_data_types_description(self, partial: bool) -> str:
        """Get description of data types to mask"""
        cfg = self.config.data_types
        
        # When doing partial mask (before substitution), mask the most sensitive items
        # that should never have realistic replacements
        if partial:
            items = []
            if cfg.ssn:
                items.append("- Social Security Numbers (SSN)")
            if cfg.passwords:
                items.append("- Passwords and security credentials")
            if cfg.financial_accounts:
                items.append("- Bank account numbers, credit card numbers")
            if cfg.medical_info:
                items.append("- Medical record numbers, diagnosis codes")
            if cfg.biometric_data:
                items.append("- Biometric identifiers")
            return "\n".join(items) if items else "- No specific types for masking"
        
        # Full mask mode - mask everything configured
        return self._get_all_data_types_description(cfg, "mask")
    
    def _get_substitution_data_types_description(self) -> str:
        """Get description of data types to substitute"""
        cfg = self.config.data_types
        
        items = []
        if cfg.names:
            items.append("- Personal names (first, last, full names)")
        if cfg.nicknames:
            items.append("- Nicknames and aliases")
        if cfg.phone_numbers:
            items.append("- Phone numbers (replace with different realistic numbers)")
        if cfg.email_addresses:
            items.append("- Email addresses (replace with different realistic addresses)")
        if cfg.physical_addresses:
            items.append("- Physical/mailing addresses")
        if cfg.dates_of_birth:
            items.append("- Dates of birth (shift by random amount)")
        if cfg.ip_addresses:
            items.append("- IP addresses")
        if cfg.usernames:
            items.append("- Usernames and handles")
        if cfg.locations:
            items.append("- Location references (cities, neighborhoods, landmarks)")
        if cfg.employers:
            items.append("- Employer names and work locations")
        if cfg.relationships:
            items.append("- Relationship identifiers (spouse name, children's names)")
        if cfg.educational_history:
            items.append("- Schools, universities, degrees")
        if cfg.physical_descriptions:
            items.append("- Physical descriptions that could identify")
        if cfg.vehicle_info:
            items.append("- Vehicle information (make, model, license plates)")
        if cfg.travel_history:
            items.append("- Travel history and frequent locations")
        
        return "\n".join(items) if items else "- General PII as appropriate"
    
    def _get_all_data_types_description(self, cfg: DataTypeConfig, mode: str) -> str:
        """Get full description of all configured data types"""
        items = []
        
        if cfg.names:
            items.append("- Personal names")
        if cfg.ssn:
            items.append("- Social Security Numbers")
        if cfg.phone_numbers:
            items.append("- Phone numbers")
        if cfg.email_addresses:
            items.append("- Email addresses")
        if cfg.physical_addresses:
            items.append("- Physical addresses")
        if cfg.dates_of_birth:
            items.append("- Dates of birth")
        if cfg.financial_accounts:
            items.append("- Financial account numbers")
        if cfg.medical_info:
            items.append("- Medical information")
        if cfg.biometric_data:
            items.append("- Biometric data")
        if cfg.ip_addresses:
            items.append("- IP addresses")
        if cfg.usernames:
            items.append("- Usernames")
        if cfg.passwords:
            items.append("- Passwords")
        if cfg.nicknames:
            items.append("- Nicknames and aliases")
        if cfg.locations:
            items.append("- Location references")
        if cfg.employers:
            items.append("- Employer information")
        if cfg.relationships:
            items.append("- Relationship identifiers")
        if cfg.educational_history:
            items.append("- Educational history")
        if cfg.physical_descriptions:
            items.append("- Physical descriptions")
        if cfg.vehicle_info:
            items.append("- Vehicle information")
        if cfg.travel_history:
            items.append("- Travel history")
        
        return "\n".join(items) if items else "- Standard PII"
    
    def _get_individuals_description(self) -> str:
        """Get description of specific individuals to target"""
        if not self.config.target_individuals:
            return ""
        
        names = ", ".join(f'"{name}"' for name in self.config.target_individuals)
        return f"""
SPECIFIC INDIVIDUALS TO ALWAYS REDACT:
The following individuals must be redacted in all forms (full name, first name, last name, nicknames, references):
{names}
"""
    
    def _get_patterns_description(self) -> str:
        """Get description of custom patterns to redact"""
        if not self.config.custom_patterns:
            return ""
        
        patterns = "\n".join(f"- Pattern: {p}" for p in self.config.custom_patterns)
        return f"""
CUSTOM PATTERNS TO REDACT:
{patterns}
"""
    
    def _get_consistency_rules(self) -> str:
        """Get substitution consistency rules"""
        rules = []
        
        if self.config.maintain_gender:
            rules.append("- Maintain apparent gender of names (male names -> male names)")
        if self.config.maintain_ethnicity_hints:
            rules.append("- Maintain cultural/ethnic characteristics of names where apparent")
        if self.config.maintain_name_length:
            rules.append("- Keep replacement names similar in length")
        
        return "\n".join(rules) if rules else "- Use any appropriate realistic replacements"
    
    def _call_llm(self, prompt: str, system_message: str) -> str:
        """Make the LLM API call"""
        model = self.config.model or config.OPENROUTER_MODEL
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "temperature": self.config.temperature,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def redact_json(self, data: dict) -> dict:
        """Convenience method to redact JSON data"""
        document = json.dumps(data, indent=2)
        redacted = self.redact(document)
        
        # Parse back to JSON
        try:
            return json.loads(redacted)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = redacted.find('{')
            end = redacted.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(redacted[start:end])
            raise ValueError("Failed to parse redacted output as JSON")


def create_redactor(
    technique: str = "both",
    sophistication: str = "standard",
    target_individuals: list = None,
    custom_patterns: list = None,
    **kwargs
) -> Redactor:
    """
    Factory function to create a configured Redactor.
    
    Args:
        technique: "mask", "substitute", or "both" (default: "both")
        sophistication: "minimal", "standard", "comprehensive", or "paranoid" (default: "standard")
        target_individuals: List of specific names to always redact
        custom_patterns: List of regex patterns to always redact
        **kwargs: Additional RedactorConfig options
    
    Returns:
        Configured Redactor instance
    """
    tech = RedactionTechnique(technique)
    soph = SophisticationLevel(sophistication)
    
    cfg = RedactorConfig(
        technique=tech,
        sophistication=soph,
        target_individuals=target_individuals or [],
        custom_patterns=custom_patterns or [],
        **kwargs
    )
    
    return Redactor(cfg)


# Default redactor with sensible defaults
default_redactor = None

def get_default_redactor() -> Redactor:
    """Get or create the default redactor instance"""
    global default_redactor
    if default_redactor is None:
        default_redactor = create_redactor()
    return default_redactor


def redact(document: str, **kwargs) -> str:
    """
    Quick redaction function with optional configuration.
    
    If no kwargs provided, uses the default redactor.
    Otherwise creates a new redactor with the specified config.
    
    Examples:
        # Simple usage with defaults
        redacted = redact("John Smith's SSN is 123-45-6789")
        
        # With configuration
        redacted = redact(doc, sophistication="paranoid", target_individuals=["Jane Doe"])
    """
    if kwargs:
        redactor = create_redactor(**kwargs)
    else:
        redactor = get_default_redactor()
    
    return redactor.redact(document)


def redact_json(data: dict, **kwargs) -> dict:
    """
    Quick JSON redaction function with optional configuration.
    
    Examples:
        redacted_data = redact_json({"name": "John Smith", "ssn": "123-45-6789"})
    """
    if kwargs:
        redactor = create_redactor(**kwargs)
    else:
        redactor = get_default_redactor()
    
    return redactor.redact_json(data)
