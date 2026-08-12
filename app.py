import json
import tempfile

import streamlit as st

from document_processor import DocumentProcessor
from ai_mapper import AIMapper
from excel_generator import ExcelGenerator


st.set_page_config(
    page_title="Tax Document Mapper",
    layout="wide"
)


st.title("Tax Document Mapper")


# =========================================================
# DATA PACK NAVIGATION
# =========================================================

st.markdown(
    """
    <a href="http://127.0.0.1:5000/data-pack.html"
       target="_self"
       style="
           display:inline-block;
           padding:10px 18px;
           background:#1f3e8b;
           color:white;
           text-decoration:none;
           border-radius:6px;
           font-weight:600;
           margin-bottom:20px;
       ">
        Data Pack HTML
    </a>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PDF UPLOAD
# =========================================================

pdf = st.file_uploader(
    "Select PDF",
    type=["pdf"]
)


# =========================================================
# PROCESS PDF
# =========================================================

if pdf:

    if st.button("Process PDF"):

        try:

            # -----------------------------------------
            # Save uploaded PDF temporarily
            # -----------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp:

                temp.write(
                    pdf.getbuffer()
                )

                pdf_path = temp.name


            # -----------------------------------------
            # PDF → TEXT
            # -----------------------------------------

            with st.spinner(
                "Reading PDF..."
            ):

                processor = DocumentProcessor()

                document_text = (
                    processor.extract_text(
                        pdf_path
                    )
                )


            # -----------------------------------------
            # TEXT → AI → PYDANTIC
            # -----------------------------------------

            with st.spinner(
                "Mapping PDF content..."
            ):

                mapper = AIMapper()

                extracted_data = (
                    mapper.map_document(
                        document_text
                    )
                )


            # -----------------------------------------
            # JSON
            # -----------------------------------------

            json_data = (
                extracted_data.model_dump(
                    by_alias=True
                )
            )


            # -----------------------------------------
            # EXCEL
            # -----------------------------------------

            template_path = (
                "Direct_Tax_Proceedings_Template.xlsx"
            )

            output_excel = (
                "Direct_Tax_Proceedings_Output.xlsx"
            )

            generator = ExcelGenerator()

            generator.generate(
                extracted_data,
                template_path,
                output_excel
            )


            # -----------------------------------------
            # RESULTS
            # -----------------------------------------

            st.success(
                "PDF processed successfully."
            )


            st.write(
                "Litigation records found:",
                len(
                    extracted_data
                    .litigation_tracker
                    .events
                )
            )


            # -----------------------------------------
            # SUMMARY PREVIEW
            # -----------------------------------------

            st.subheader(
                "Summary Details"
            )

            st.json(
                json_data[
                    "summary_details"
                ]
            )


            # -----------------------------------------
            # LITIGATION PREVIEW
            # -----------------------------------------

            st.subheader(
                "Litigation Tracker"
            )

            st.json(
                json_data[
                    "litigation_tracker"
                ]
            )


            # -----------------------------------------
            # JSON DOWNLOAD
            # -----------------------------------------

            st.download_button(
                label="Download JSON",
                data=json.dumps(
                    json_data,
                    indent=4,
                    ensure_ascii=False
                ),
                file_name="extracted_data.json",
                mime="application/json"
            )


            # -----------------------------------------
            # EXCEL DOWNLOAD
            # -----------------------------------------

            with open(
                output_excel,
                "rb"
            ) as excel_file:

                st.download_button(
                    label="Download Excel",
                    data=excel_file,
                    file_name=output_excel,
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.spreadsheetml.sheet"
                    )
                )


        except Exception as error:

            st.error(
                f"Processing failed: {error}"
            )
