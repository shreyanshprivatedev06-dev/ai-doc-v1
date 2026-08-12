from typing import List, Optional
from pydantic import BaseModel, Field


class SummaryDetails(BaseModel):

    name_of_company_group: Optional[str] = Field(
        None,
        alias="Name of Company Group"
    )

    name_of_entity: Optional[str] = Field(
        None,
        alias="Name of Entity"
    )

    starting_year: Optional[str] = Field(
        None,
        alias="Starting Year (YYYY-YY)"
    )

    applicable_type_of_laws: Optional[str] = Field(
        None,
        alias="Applicable Type of Laws"
    )

    applicable_nature_of_proceedings: Optional[str] = Field(
        None,
        alias="Applicable Nature of Proceedings"
    )

    applicable_forum_authority: Optional[str] = Field(
        None,
        alias="Applicable Forum/ Authority"
    )

    applicable_issue: Optional[str] = Field(
        None,
        alias="Applicable Issue"
    )

    applicable_cases: Optional[str] = Field(
        None,
        alias="Applicable Cases"
    )


class LitigationDetails(BaseModel):

    record_status: Optional[str] = Field(
        None,
        alias="Record Status"
    )

    period: Optional[str] = Field(
        None,
        alias="Period"
    )

    type_of_law: Optional[str] = Field(
        None,
        alias="Type of Law"
    )

    case_name: Optional[str] = Field(
        None,
        alias="Case Name"
    )

    nature_of_proceedings: Optional[str] = Field(
        None,
        alias="Nature of Proceedings"
    )

    authority: Optional[str] = Field(
        None,
        alias="Authority"
    )

    issue: Optional[str] = Field(
        None,
        alias="Issue"
    )

    issue_description: Optional[str] = Field(
        None,
        alias="Issue Description"
    )

    transfer_pricing_issue: Optional[str] = Field(
        None,
        alias="Is it Transfer Pricing issue?"
    )

    base_disallowance_amount: Optional[str] = Field(
        None,
        alias="Base / Disallowance Amount"
    )

    existing_liability: Optional[str] = Field(
        None,
        alias="Existing Liability"
    )

    tax_duty: Optional[str] = Field(
        None,
        alias="Tax / Duty"
    )

    interest: Optional[str] = Field(
        None,
        alias="Interest"
    )

    penalty: Optional[str] = Field(
        None,
        alias="Penalty"
    )

    risk_assessment: Optional[str] = Field(
        None,
        alias="Risk Assessment"
    )

    provision_created: Optional[str] = Field(
        None,
        alias="Provision created"
    )

    contingent_liability: Optional[str] = Field(
        None,
        alias="Whether a Contingent liability?"
    )

    contingent_liability_amount: Optional[str] = Field(
        None,
        alias="Contingent liability (Amount)"
    )

    first_notice_appeal_date: Optional[str] = Field(
        None,
        alias="First Notice / Appeal date"
    )

    date_of_order: Optional[str] = Field(
        None,
        alias="Date of Order"
    )

    status: Optional[str] = Field(
        None,
        alias="Status"
    )

    country: Optional[str] = Field(
        None,
        alias="Country"
    )

    entity_name: Optional[str] = Field(
        None,
        alias="Entity name"
    )

    notice_received_from: Optional[str] = Field(
        None,
        alias="Notice received from"
    )

    years_notice_pertains_to: Optional[str] = Field(
        None,
        alias="Years for which the Notice pertains (If applicable for multi years)"
    )

    currency: Optional[str] = Field(
        None,
        alias="Currency"
    )

    demand_paid_amount: Optional[str] = Field(
        None,
        alias="Demand Paid Amount (Local Currency)"
    )

    provision_required: Optional[str] = Field(
        None,
        alias="Whether Provision required (Yes/ No)"
    )

    provision_created_level: Optional[str] = Field(
        None,
        alias="Provision created level - Local books/Group books"
    )

    contingent_liability_created_level: Optional[str] = Field(
        None,
        alias="Contingent liability created level - Local books/Group books"
    )


class LitigationTracker(BaseModel):

    events: List[LitigationDetails] = Field(
        default_factory=list
    )


class ExtractedDocument(BaseModel):

    summary_details: SummaryDetails

    litigation_tracker: LitigationTracker