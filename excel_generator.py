from pathlib import Path
from copy import copy

from openpyxl import load_workbook
from openpyxl.formula.translate import Translator


class ExcelGenerator:

    # ============================================================
    # GENERATE EXCEL
    # ============================================================

    def generate(
        self,
        extracted_data,
        template_path,
        output_path
    ):

        template_path = Path(template_path)
        output_path = Path(output_path)

        # --------------------------------------------------------
        # CHECK TEMPLATE
        # --------------------------------------------------------

        if not template_path.exists():

            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        # --------------------------------------------------------
        # LOAD EXISTING TEMPLATE
        #
        # IMPORTANT:
        # We NEVER create a new workbook.
        # --------------------------------------------------------

        workbook = load_workbook(
            template_path
        )

        # --------------------------------------------------------
        # VERIFY EXISTING SHEETS
        # --------------------------------------------------------

        required_sheets = [
            "Summary_Table 1",
            "Litigation Tracker_Table 1"
        ]

        for sheet_name in required_sheets:

            if sheet_name not in workbook.sheetnames:

                raise ValueError(
                    f"Required template sheet "
                    f"'{sheet_name}' was not found."
                )

        # --------------------------------------------------------
        # GET EXISTING WORKSHEETS
        # --------------------------------------------------------

        summary_ws = workbook[
            "Summary_Table 1"
        ]

        litigation_ws = workbook[
            "Litigation Tracker_Table 1"
        ]

        # ========================================================
        # SUMMARY
        # ========================================================

        summary = (
            extracted_data.summary_details
        )

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # These are EXISTING cells in your template.
        # We only populate them.
        #
        # No formatting is created here.
        # --------------------------------------------------------

        summary_values = {

            "D2":
                summary.name_of_company_group,

            "D4":
                summary.name_of_entity,

            "D6":
                summary.starting_year,

            "D8":
                summary.applicable_type_of_laws,

            "D12":
                summary.applicable_nature_of_proceedings,

            "D16":
                summary.applicable_forum_authority,

            "D20":
                summary.applicable_issue,

            "D24":
                summary.applicable_cases,
        }

        for cell_address, value in summary_values.items():

            if value is None:
                value = ""

            summary_ws[
                cell_address
            ].value = value

        # ========================================================
        # LITIGATION TRACKER
        # ========================================================

        events = (
            extracted_data
            .litigation_tracker
            .events
        )

        # --------------------------------------------------------
        # DATA START ROW
        #
        # Your template:
        #
        # Row 1 = main headers
        # Row 2 = detailed headers / descriptions
        # Row 3 = template/example row
        # Row 4 onward = actual data
        # --------------------------------------------------------

        start_row = 4

        # --------------------------------------------------------
        # BUILD HEADER MAP
        #
        # We inspect the EXISTING TEMPLATE instead of creating
        # our own column order.
        # --------------------------------------------------------

        header_map = self._build_header_map(
            litigation_ws
        )

        # --------------------------------------------------------
        # EXISTING TEMPLATE DATA ROW
        #
        # Formatting for additional records will be copied
        # from this row.
        # --------------------------------------------------------

        template_data_row = start_row

        # --------------------------------------------------------
        # WRITE EACH LITIGATION EVENT
        # --------------------------------------------------------

        current_row = start_row

        for event in events:

            rows_used = (
                self._write_event(
                    worksheet=litigation_ws,
                    event=event,
                    header_map=header_map,
                    start_row=current_row,
                    template_row=template_data_row
                )
            )

            current_row += rows_used

        # ========================================================
        # SAVE
        # ========================================================

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        workbook.save(
            output_path
        )


    # ============================================================
    # BUILD HEADER MAP
    # ============================================================

    def _build_header_map(
        self,
        worksheet
    ):

        header_map = {}

        # --------------------------------------------------------
        # FIRST TRY ROW 2
        #
        # The detailed headers in the template are preferable
        # because they contain the complete field names.
        # --------------------------------------------------------

        for cell in worksheet[2]:

            if cell.value is None:
                continue

            header = self._normalize_header(
                cell.value
            )

            if header:

                header_map[header] = (
                    cell.column
                )

        # --------------------------------------------------------
        # FALLBACK TO ROW 1
        #
        # Only add headers which are not already present.
        # --------------------------------------------------------

        for cell in worksheet[1]:

            if cell.value is None:
                continue

            header = self._normalize_header(
                cell.value
            )

            if header and header not in header_map:

                header_map[header] = (
                    cell.column
                )

        return header_map


    # ============================================================
    # WRITE ONE LITIGATION EVENT
    # ============================================================

    def _write_event(
        self,
        worksheet,
        event,
        header_map,
        start_row,
        template_row
    ):

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Values are mapped to the ACTUAL template headers.
        #
        # There is no manually constructed Excel column sequence.
        # --------------------------------------------------------

        values = {

            "Record Status":
                event.record_status,

            "Period":
                event.period,

            "Type of Law":
                event.type_of_law,

            "Case Name":
                event.case_name,

            "Nature of Proceedings":
                event.nature_of_proceedings,

            "Authority":
                event.authority,

            "Issue":
                event.issue,

            "Issue Description":
                event.issue_description,

            "Is it Transfer Pricing issue?":
                event.transfer_pricing_issue,

            "Base / Disallowance Amount":
                event.base_disallowance_amount,

            "Existing Liability":
                event.existing_liability,

            "Tax / Duty":
                event.tax_duty,

            "Interest":
                event.interest,

            "Penalty":
                event.penalty,

            "Risk Assessment":
                event.risk_assessment,

            "Provision created":
                event.provision_created,

            "Whether a Contingent liability?":
                event.contingent_liability,

            "Contingent liability (Amount)":
                event.contingent_liability_amount,

            "First Notice / Appeal date":
                event.first_notice_appeal_date,

            "Date of Order":
                event.date_of_order,

            "Status":
                event.status,

            "Country":
                event.country,

            "Entity name":
                event.entity_name,

            "Notice received from":
                event.notice_received_from,

            "Years for which the Notice pertains (If applicable for multi years)":
                event.years_notice_pertains_to,

            "Currency":
                event.currency,

            "Demand Paid Amount":
                event.demand_paid_amount,

            "Whether Provision required":
                event.provision_required,

            "Provision created level":
                event.provision_created_level,

            "Contingent liability created level":
                event.contingent_liability_created_level,
        }

        # --------------------------------------------------------
        # NORMALIZE VALUES
        #
        # Example:
        #
        # "Income Tax Department\nCommissioner of Income Tax"
        #
        # becomes:
        #
        # [
        #     "Income Tax Department",
        #     "Commissioner of Income Tax"
        # ]
        #
        # NO COMMA IS ADDED.
        # --------------------------------------------------------

        normalized_values = {}

        maximum_rows = 1

        for header, value in values.items():

            value_list = self._split_values(
                value
            )

            normalized_values[
                header
            ] = value_list

            maximum_rows = max(
                maximum_rows,
                len(value_list)
            )

        # --------------------------------------------------------
        # WRITE EACH VALUE TO ITS OWN ROW
        # --------------------------------------------------------

        for row_offset in range(
            maximum_rows
        ):

            row_number = (
                start_row +
                row_offset
            )

            # ----------------------------------------------------
            # Copy template formatting when the row does not
            # already exist as a formatted template row.
            # ----------------------------------------------------

            if row_number != template_row:

                self._copy_template_row(
                    worksheet,
                    template_row,
                    row_number
                )

            # ----------------------------------------------------
            # WRITE VALUES
            # ----------------------------------------------------

            for header, value_list in (
                normalized_values.items()
            ):

                normalized_header = (
                    self._normalize_header(
                        header
                    )
                )

                # ------------------------------------------------
                # Find exact template column.
                # ------------------------------------------------

                column = self._find_column(
                    header_map,
                    normalized_header
                )

                if column is None:
                    continue

                # ------------------------------------------------
                # Get value for this row.
                #
                # If this particular field has fewer values
                # than another field, leave the cell blank.
                # ------------------------------------------------

                value = ""

                if (
                    row_offset <
                    len(value_list)
                ):

                    value = value_list[
                        row_offset
                    ]

                worksheet.cell(
                    row=row_number,
                    column=column
                ).value = value

        return maximum_rows


    # ============================================================
    # SPLIT MULTIPLE VALUES
    # ============================================================

    def _split_values(
        self,
        value
    ):

        if value is None:

            return [""]

        # --------------------------------------------------------
        # Pydantic / AI may already return a list.
        # --------------------------------------------------------

        if isinstance(
            value,
            (list, tuple)
        ):

            result = []

            for item in value:

                if item is None:
                    continue

                text = str(
                    item
                ).strip()

                if text:
                    result.append(
                        text
                    )

            return result or [""]

        # --------------------------------------------------------
        # Normal string
        # --------------------------------------------------------

        text = str(
            value
        ).strip()

        if not text:

            return [""]

        # --------------------------------------------------------
        # Split line-separated values.
        #
        # IMPORTANT:
        # We DO NOT split on commas.
        #
        # Therefore:
        #
        # "A, B, C"
        #
        # remains one value.
        #
        # But:
        #
        # "A
        #  B
        #  C"
        #
        # becomes three rows.
        # --------------------------------------------------------

        if "\n" in text:

            result = [
                item.strip()
                for item in text.splitlines()
                if item.strip()
            ]

            return result or [""]

        return [text]


    # ============================================================
    # NORMALIZE HEADER
    # ============================================================

    def _normalize_header(
        self,
        value
    ):

        if value is None:
            return ""

        text = str(
            value
        ).strip()

        # Normalize whitespace.
        text = " ".join(
            text.split()
        )

        # Normalize common template punctuation
        # differences without changing the workbook.
        text = text.replace(
            "  ",
            " "
        )

        return text.lower()


    # ============================================================
    # FIND TEMPLATE COLUMN
    # ============================================================

    def _find_column(
        self,
        header_map,
        normalized_header
    ):

        # --------------------------------------------------------
        # Exact normalized match.
        # --------------------------------------------------------

        if normalized_header in header_map:

            return header_map[
                normalized_header
            ]

        # --------------------------------------------------------
        # Known variations.
        #
        # These only resolve differences between the Pydantic
        # field label and the actual template header.
        # --------------------------------------------------------

        aliases = {

            "is it transfer pricing issue?":
                [
                    "is it transfer pricing issue?",
                    "is it transfer pricing issue"
                ],

            "base / disallowance amount":
                [
                    "base / disallowance amount",
                    "base disallowance amount"
                ],

            "existing liability":
                [
                    "existing liability",
                    "total existing amount"
                ],

            "whether a contingent liability?":
                [
                    "whether a contingent liability?",
                    "contingent liability"
                ],

            "first notice / appeal date":
                [
                    "first notice / appeal date",
                    "matter start date"
                ],

            "date of order":
                [
                    "date of order",
                    "matter end date"
                ],

            "notice received from":
                [
                    "notice received from",
                    "notice recieved from"
                ],

            "provision created level":
                [
                    "provision created level",
                    "provision created level - local books/group books"
                ],

            "contingent liability created level":
                [
                    "contingent liability created level",
                    "contingent liability created level - local books/group books"
                ],
        }

        possible_headers = aliases.get(
            normalized_header,
            [normalized_header]
        )

        for possible in possible_headers:

            possible = self._normalize_header(
                possible
            )

            if possible in header_map:

                return header_map[
                    possible
                ]

        return None


    # ============================================================
    # COPY TEMPLATE ROW FORMATTING
    # ============================================================

    def _copy_template_row(
        self,
        worksheet,
        source_row,
        target_row
    ):

        # --------------------------------------------------------
        # Copy row height.
        # --------------------------------------------------------

        source_dimension = (
            worksheet.row_dimensions[
                source_row
            ]
        )

        target_dimension = (
            worksheet.row_dimensions[
                target_row
            ]
        )

        target_dimension.height = (
            source_dimension.height
        )

        target_dimension.hidden = (
            source_dimension.hidden
        )

        # --------------------------------------------------------
        # Copy cells.
        # --------------------------------------------------------

        for column in range(
            1,
            worksheet.max_column + 1
        ):

            source = worksheet.cell(
                row=source_row,
                column=column
            )

            target = worksheet.cell(
                row=target_row,
                column=column
            )

            # ----------------------------------------------------
            # Copy formatting.
            # ----------------------------------------------------

            if source.has_style:

                target._style = copy(
                    source._style
                )

            if source.number_format:

                target.number_format = (
                    source.number_format
                )

            if source.alignment:

                target.alignment = copy(
                    source.alignment
                )

            if source.protection:

                target.protection = copy(
                    source.protection
                )

            # ----------------------------------------------------
            # Copy hyperlink if present.
            # ----------------------------------------------------

            if source.hyperlink:

                target._hyperlink = copy(
                    source.hyperlink
                )

            # ----------------------------------------------------
            # Copy comments if present.
            # ----------------------------------------------------

            if source.comment:

                target.comment = copy(
                    source.comment
                )

            # ----------------------------------------------------
            # Copy formula with translated row reference.
            #
            # We do NOT copy ordinary values because those may
            # be example/template data.
            # ----------------------------------------------------

            if (
                isinstance(
                    source.value,
                    str
                )
                and source.value.startswith("=")
            ):

                try:

                    target.value = (
                        Translator(
                            source.value,
                            origin=source.coordinate
                        ).translate_formula(
                            target.coordinate
                        )
                    )

                except Exception:

                    target.value = (
                        source.value
                    )

            else:

                target.value = None