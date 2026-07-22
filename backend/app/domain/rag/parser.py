import io

class DocumentParser:
    """Extracts raw text content from PDF, DOCX, and TXT files."""

    @classmethod
    def parse(cls, filename: str, content_bytes: bytes, mime_type: str) -> str:
        filename_lower = filename.lower()

        if filename_lower.endswith(".pdf") or "pdf" in mime_type:
            return cls._parse_pdf(content_bytes)
        elif filename_lower.endswith(".docx") or "officedocument" in mime_type:
            return cls._parse_docx(content_bytes)
        else:
            # Fallback to UTF-8 plain text decoding
            try:
                return content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return content_bytes.decode("latin-1", errors="ignore")

    @classmethod
    def _parse_pdf(cls, content_bytes: bytes) -> str:
        """Parses PDF bytes into clean text."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            text_runs = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_runs.append(extracted)
            return "\n".join(text_runs)
        except Exception as e:
            print(f"pypdf extraction warning: {e}")
            return content_bytes.decode("utf-8", errors="ignore")

    @classmethod
    def _parse_docx(cls, content_bytes: bytes) -> str:
        """Parses DOCX bytes into plain text."""
        try:
            import docx2txt
            return docx2txt.process(io.BytesIO(content_bytes))
        except Exception as e:
            print(f"docx extraction warning: {e}")
            return content_bytes.decode("utf-8", errors="ignore")
