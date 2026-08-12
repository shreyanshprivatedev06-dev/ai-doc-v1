import json
import tempfile
from pathlib import Path
import os

import streamlit as st

from document_processor import DocumentProcessor
from ai_mapper import AIMapper
from excel_generator import ExcelGenerator


# ============================================================
# CONFIGURATION
# ============================================================


st.set_page_config(
    page_title="Tax Document Mapper",
    layout="wide"
)


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# EXACT EXCEL TEMPLATE
# ============================================================

TEMPLATE_PATH = (
    BASE_DIR /
    "Direct_Tax_Proceedings_Template.xlsx"
)


# ============================================================
# PAGE
# ============================================================

st.title("Tax Document Mapper")


# ============================================================
# PDF UPLOAD
# ============================================================

pdf = st.file_uploader(
    "Select PDF",
    type=["pdf"]
)


# ============================================================
# PROCESS
# ============================================================

if pdf:

    if st.button("Process PDF"):

        try:

            # ==================================================
            # CHECK TEMPLATE
            # ==================================================

            if not TEMPLATE_PATH.exists():

                raise FileNotFoundError(
                    "The Excel template was not found.\n\n"
                    f"Expected location:\n"
                    f"{TEMPLATE_PATH}"
                )


            # ==================================================
            # SAVE PDF TEMPORARILY
            # ==================================================

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp:

                temp.write(
                    pdf.getbuffer()
                )

                pdf_path = temp.name


            # ==================================================
            # PDF → TEXT
            # ==================================================

            with st.spinner(
                "Reading PDF..."
            ):

                processor = DocumentProcessor()

                document_text = (
                    processor.extract_text(
                        pdf_path
                    )
                )


            # ==================================================
            # TEXT → AI → PYDANTIC
            # ==================================================

            with st.spinner(
                "Mapping PDF content..."
            ):

                mapper = AIMapper()

                extracted_data = (
                    mapper.map_document(
                        document_text
                    )
                )


            # ==================================================
            # JSON
            # ==================================================

            json_data = (
                extracted_data.model_dump(
                    by_alias=True
                )
            )


            # ==================================================
            # OUTPUT FILE
            # ==================================================

            output_excel = (
                BASE_DIR /
                "Direct_Tax_Proceedings_Output.xlsx"
            )


            # ==================================================
            # TEMPLATE → FILLED EXCEL
            # ==================================================

            with st.spinner(
                "Filling the Excel template..."
            ):

                generator = ExcelGenerator()

                generator.generate(
                    extracted_data,
                    str(TEMPLATE_PATH),
                    str(output_excel)
                )


            # ==================================================
            # SUCCESS
            # ==================================================

            st.success(
                "PDF processed successfully."
            )


            # ==================================================
            # LITIGATION COUNT
            # ==================================================

            litigation_count = len(
                extracted_data
                .litigation_tracker
                .events
            )

            st.write(
                "Litigation records found:",
                litigation_count
            )


            # ==================================================
            # SUMMARY PREVIEW
            # ==================================================

            st.subheader(
                "Summary Details"
            )

            st.json(
                json_data[
                    "summary_details"
                ]
            )


            # ==================================================
            # LITIGATION PREVIEW
            # ==================================================

            st.subheader(
                "Litigation Tracker"
            )

            st.json(
                json_data[
                    "litigation_tracker"
                ]
            )


            # ==================================================
            # JSON DOWNLOAD
            # ==================================================

            json_download = json.dumps(
                json_data,
                indent=4,
                ensure_ascii=False
            )

            st.download_button(
                label="Download JSON",
                data=json_download,
                file_name="extracted_data.json",
                mime="application/json"
            )


            # ==================================================
            # EXCEL DOWNLOAD
            # ==================================================

            with open(
                output_excel,
                "rb"
            ) as excel_file:

                excel_data = (
                    excel_file.read()
                )


            st.download_button(
                label="Download Completed Excel",
                data=excel_data,
                file_name=(
                    "Direct_Tax_Proceedings_Output.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                )
            )


        except Exception as error:

            st.error(
                f"Processing failed: {error}"
            )