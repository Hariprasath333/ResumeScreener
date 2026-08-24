import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.core.exceptions import LLMValidationError

T = TypeVar("T", bound=BaseModel)


class LLMValidator:
    """Validates raw LLM outputs against Pydantic schemas and business constraints."""

    @staticmethod
    def clean_json_string(raw_response: str) -> str:
        """Strips markdown markdown codeblocks e.g. ```json ... ``` from LLM response."""
        if not raw_response:
            return "{}"

        cleaned = raw_response.strip()
        # Remove ```json and ```
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def parse_and_validate(self, raw_response: str, schema_cls: Type[T]) -> T:
        """
        Parses raw text into JSON and validates against target Pydantic schema class.
        Throws LLMValidationError on invalid format or constraint violation.
        """
        cleaned_json = self.clean_json_string(raw_response)

        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise LLMValidationError(f"LLM output is not valid JSON: {str(e)}", details={"raw": raw_response})

        try:
            validated_obj = schema_cls.model_validate(data)
            return validated_obj
        except ValidationError as e:
            raise LLMValidationError(f"Pydantic validation failed: {str(e)}", details={"errors": e.errors()})
