from app.core.exceptions import CorruptedFileError, ResumeParsingError


class TextParser:
    """Plain text parser for TXT resumes."""

    def parse(self, file_path_or_bytes) -> dict:
        """
        Parses text content from string, bytes, or file path.
        """
        try:
            if isinstance(file_path_or_bytes, bytes):
                try:
                    raw_text = file_path_or_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    raw_text = file_path_or_bytes.decode("latin-1", errors="ignore")
            elif isinstance(file_path_or_bytes, str):
                raw_text = file_path_or_bytes
            else:
                raise CorruptedFileError("Invalid text file payload")

            raw_text = raw_text.strip()
            if not raw_text:
                raise ResumeParsingError("Uploaded text file is empty")

            return {
                "raw_text": raw_text,
                "pages_count": 1,
                "ocr_used": False,
                "confidence": 1.0
            }
        except Exception as e:
            if isinstance(e, (CorruptedFileError, ResumeParsingError)):
                raise e
            raise ResumeParsingError(f"Failed to parse text resume: {str(e)}")
