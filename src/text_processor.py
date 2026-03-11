"""Text post-processing for spoken punctuation."""

import re


class TextPostProcessor:
    """Post-process transcription text to convert spoken punctuation."""

    # Patterns for spoken punctuation conversion
    REPLACEMENTS = [
        (r"\bperiod\b", "."),
        (r"\bfull stop\b", "."),
        (r"\b[ck]a?r?ma\b", ","),  # Handles "comma", "karma"
        (r"\bcomma\b", ","),
        (r"\bquestion mark\b", "?"),
        (r"\bexclamation mark\b", "!"),
        (r"\bexclamation point\b", "!"),
        (r"\bcolon\b", ":"),
        (r"\bsemicolon\b", ";"),
        (r"\bsemi colon\b", ";"),
        (r"\bellipsis\b", "..."),
        (r"\bdash\b", " —"),
        (r"\bhyphen\b", "-"),
        (r"\bopen quote\b", '"'),
        (r"\bclose quote\b", '"'),
        (r"\bopen paren\b", "("),
        (r"\bclose paren\b", ")"),
        (r"\bnew line\b", "\n"),
        (r"\bnewline\b", "\n"),
        (r"\bnew paragraph\b", "\n\n"),
    ]

    @classmethod
    def process(cls, text: str) -> str:
        """
        Process text to convert spoken punctuation to actual punctuation.
        
        Args:
            text: Raw transcription text
        
        Returns:
            Processed text with punctuation converted
        """
        result = text
        
        # Apply replacements (case-insensitive)
        for pattern, replacement in cls.REPLACEMENTS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Fix spacing around punctuation
        result = cls._fix_spacing_around_punctuation(result)
        
        # Ensure space after punctuation
        result = cls._ensure_space_after_punctuation(result)
        
        return result

    @staticmethod
    def _fix_spacing_around_punctuation(text: str) -> str:
        """Remove spaces before punctuation marks."""
        # Remove spaces before .,?!:;
        result = re.sub(r"\s+([.,?!:;])", r"\1", text)
        return result

    @staticmethod
    def _ensure_space_after_punctuation(text: str) -> str:
        """Ensure there's a space after punctuation marks (except for certain cases)."""
        # Add space after .,?!:; if followed by a word character
        result = re.sub(r"([.,?!:;])(\w)", r"\1 \2", text)
        return result
