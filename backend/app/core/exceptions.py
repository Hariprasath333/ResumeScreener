class ScreenerBaseException(Exception):
    """Base exception for Smart Resume Screener application."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CorruptedFileError(ScreenerBaseException):
    """Raised when an uploaded file is corrupted or unreadable."""
    pass


class ResumeParsingError(ScreenerBaseException):
    """Raised when text extraction or profile parsing fails."""
    pass


class LLMValidationError(ScreenerBaseException):
    """Raised when LLM output fails schema validation or business rules."""
    pass


class ResourceNotFoundError(ScreenerBaseException):
    """Raised when a DB entity (Job, Resume, Candidate, Match) is missing."""
    pass


class JobNotFoundError(ResourceNotFoundError):
    pass


class ResumeNotFoundError(ResourceNotFoundError):
    pass


class MatchNotFoundError(ResourceNotFoundError):
    pass
