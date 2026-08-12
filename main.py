import json
from pathlib import Path

from dotenv import load_dotenv

from document_processor import DocumentProcessor
from ai_mapper import AIMapper
from excel_generator import ExcelGenerator


def save_json(data, path):

    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    load_dotenv()

    pdf_path = "input/document.pdf"
    json_path = "output/extracted.json"
    excel_path = "output/litigation_report.xlsx"

    # 1. PDF → Text
    document_processor = DocumentProcessor()

    document_text = document_processor.extract_text(
        pdf_path
    )

    if not document_text.strip():
        raise ValueError(
            "No text found in PDF."
        )

    # 2. Text → Structured Schema
    ai_mapper = AIMapper()

    extracted_data = ai_mapper.map_document(
        document_text
    )

    # 3. Schema → JSON
    extracted_json = extracted_data.model_dump()

    save_json(
        extracted_json,
        json_path
    )

    # 4. Schema → Excel
    excel_generator = ExcelGenerator()

    excel_generator.generate(
        extracted_data,
        excel_path
    )

    print("Processing completed successfully.")


if __name__ == "__main__":
    main()