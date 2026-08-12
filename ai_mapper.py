import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import ExtractedDocument


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# AI MAPPER
# ============================================================

class AIMapper:

    def __init__(self):

        # ====================================================
        # TEMPORARY HARDCODED API KEY
        # ====================================================
        # Replace the value below with your NEW OpenAI API key.
        #
        # IMPORTANT:
        # Do NOT use the API key that GitHub previously detected.
        # ====================================================

        api_key = "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"

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=api_key
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4.1"
        )


    # ========================================================
    # MAP DOCUMENT
    # ========================================================

    def map_document(
        self,
        document_text: str
    ) -> ExtractedDocument:

        system_prompt = """
You are an expert tax litigation document
extraction system.

Your task is to analyze the supplied PDF text
and populate TWO separate sections:

1. Summary Details
2. Litigation Tracker

Extract one company/entity-level summary.

The Summary Details fields are:

- Name of the Company
- Name of Entity
- Starting year
- Applicable proceedings
- Applicable forum
- Applicable issues
- Applicable cases

There must be ONLY ONE Summary Details object.

Do not create multiple summaries just because
the company appears multiple times in the document.

Identify every DISTINCT litigation/proceeding
matter in the document.

Each separate matter must become exactly ONE
LitigationDetails event.

A matter may be identified using differences in:

- Period
- Type of Law
- Nature of Proceeding
- Authority
- Issue
- Notice
- Order
- Appeal
- Status
- Case/reference information

If the same litigation matter is mentioned
multiple times in the PDF, combine the information
into ONE event.

DO NOT create duplicate events.

1. Extract only information actually present
   in the document.

2. Never invent or infer unsupported facts.

3. If a field is not available, return null.

4. Preserve dates as they appear in the source
   where possible.

5. Preserve monetary amounts accurately.

6. Do not confuse a tax amount with an interest,
   penalty, provision or contingent liability amount.

7. Do not treat ordinary business information
   as litigation.

8. Do not treat an invoice, purchase order,
   sales transaction or ordinary tax reference
   as a litigation event unless the document
   clearly connects it to a proceeding.

9. If the document contains tables, paragraphs
   and bullet points, consider all of them.

10. Information can be distributed across
    multiple pages. Combine related information.

11. Do not create a new litigation event simply
    because the same case is mentioned in a
    different section.

12. A closed/historical matter is still a
    litigation event if it is presented as a
    distinct matter.

13. If a field explicitly says "Not Applicable",
    "N/A", "None", etc., preserve that meaning.

14. If a date has not occurred or is explicitly
    unavailable, return null rather than inventing
    a date.

15. Keep Issue concise but sufficiently descriptive.

Before returning the result:

- Check that there is exactly one summary.
- Check that each distinct litigation matter
  appears only once.
- Check that repeated mentions of the same
  matter have been merged.
- Check that irrelevant business information
  has not been converted into litigation events.
- Check that all available fields are populated.
"""

        # ====================================================
        # OPENAI STRUCTURED OUTPUT
        # ====================================================

        response = self.client.responses.parse(
            model=self.model,

            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze the following PDF content "
                        "and map it to the required schemas.\n\n"
                        f"{document_text}"
                    )
                }
            ],

            text_format=ExtractedDocument
        )

        # ====================================================
        # RETURN PYDANTIC RESULT
        # ====================================================

        return response.output_parsed
