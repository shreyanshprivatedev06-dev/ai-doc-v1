from pypdf import PdfReader


class DocumentProcessor:

    def extract_text(self, pdf_path: str) -> str:

        reader = PdfReader(pdf_path)

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text() or ""

            pages.append(
                f"\n--- PAGE {page_number} ---\n"
                f"{text}"
            )

        return "\n".join(pages)