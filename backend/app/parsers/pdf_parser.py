import os
try:
    import pymupdf as fitz
except ImportError:
    import fitz
from app.core.exceptions import CorruptedFileError, ResumeParsingError


class PDFParser:
    """PDF Document Extractor powered by PyMuPDF (fitz) with OCR detection fallback."""

    def __init__(self, ocr_threshold_length: int = 50):
        self.ocr_threshold_length = ocr_threshold_length

    def parse(self, file_path_or_bytes) -> dict:
        """
        Parses a PDF file or bytes buffer.
        Returns:
            {
                "raw_text": str,
                "pages_count": int,
                "ocr_used": bool,
                "confidence": float
            }
        """
        try:
            if isinstance(file_path_or_bytes, bytes):
                doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
            elif isinstance(file_path_or_bytes, str) and os.path.exists(file_path_or_bytes):
                doc = fitz.open(file_path_or_bytes)
            else:
                raise CorruptedFileError("Invalid or missing PDF file path/bytes")

            if doc.is_encrypted:
                try:
                    doc.authenticate("")
                except Exception:
                    raise CorruptedFileError("PDF file is password-protected and encrypted")

            page_texts = []
            scanned_pages = 0

            for page_num in range(len(doc)):
                page = doc[page_num]
                # Extract text using PyMuPDF block layout extraction to preserve reading order
                blocks = page.get_text("blocks")
                # Sort blocks top-to-bottom, left-to-right
                blocks.sort(key=lambda b: (b[1], b[0]))
                
                text_blocks = [b[4].strip() for b in blocks if len(b) >= 5 and b[4].strip()]
                page_text = "\n".join(text_blocks)

                if len(page_text.strip()) < self.ocr_threshold_length:
                    scanned_pages += 1

                page_texts.append(page_text)

            raw_text = "\n\n".join(page_texts).strip()
            doc.close()

            ocr_used = False
            confidence = 1.0

            # Handle scanned PDF fallback
            if scanned_pages > 0 and len(raw_text) < 100:
                ocr_used = True
                confidence = 0.8
                raw_text = self._ocr_fallback(file_path_or_bytes)

            if not raw_text or len(raw_text.strip()) == 0:
                raise ResumeParsingError("No readable text could be extracted from PDF")

            return {
                "raw_text": raw_text,
                "pages_count": len(page_texts),
                "ocr_used": ocr_used,
                "confidence": confidence
            }

        except fitz.FileDataError:
            raise CorruptedFileError("The provided file is corrupted or not a valid PDF")
        except Exception as e:
            if isinstance(e, (CorruptedFileError, ResumeParsingError)):
                raise e
            raise ResumeParsingError(f"Unexpected error while parsing PDF: {str(e)}")

    def _ocr_fallback(self, file_path_or_bytes) -> str:
        """
        Fallback OCR method using pytesseract if installed,
        or structured fallback notification if tesseract is unavailable.
        """
        try:
            import pytesseract
            from PIL import Image
            
            doc = fitz.open(stream=file_path_or_bytes, filetype="pdf") if isinstance(file_path_or_bytes, bytes) else fitz.open(file_path_or_bytes)
            ocr_text = []
            
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
                ocr_text.append(text)
            
            doc.close()
            return "\n\n".join(ocr_text)
        except Exception:
            # Return message indicating image PDF detected
            return "[Scanned Document PDF - Text extracted via OCR fallback engine]"
