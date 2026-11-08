"""The rubric: what a DPDP consent notice must contain, one check per requirement.

Every check cites the Digital Personal Data Protection Act, 2023 ("the Act") or the
Digital Personal Data Protection Rules, 2025 (G.S.R. 846(E), 13 Nov 2025, "the Rules").

The rubric only covers what the law asks a *notice* to say. It does not check whether
the processing itself is lawful, and it does not reward extra content.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    id: str
    title: str
    requirement: str  # what the notice must do, in plain words
    passes_if: str  # guidance for the judge
    fails_if: str  # guidance for the judge
    cites: str
    children_only: bool = False


CHECKS: tuple[Check, ...] = (
    Check(
        id="data_itemised",
        title="Lists the personal data, item by item",
        requirement="An itemised description of the personal data that will be processed.",
        passes_if="The notice lists the personal data as separate, concrete items, and every data category in the business facts appears.",
        fails_if="The list is vague ('information such as…', 'and other details'), or one or more data categories from the business facts are missing.",
        cites="Act s.5(1)(i); Rules r.3(b)(i)",
    ),
    Check(
        id="purpose_specific",
        title="States specific purposes",
        requirement="The specified purpose(s) of processing, and a specific description of the goods or services or uses it enables.",
        passes_if="Each purpose is specific and tied to the service described in the business facts.",
        fails_if="A purpose is a catch-all ('any other purpose', 'business purposes', 'as we deem fit', 'any lawful purpose'), or the purposes are only a generic phrase like 'to provide and improve our services'.",
        cites="Act s.5(1)(i); Rules r.3(b)(ii)",
    ),
    Check(
        id="withdraw_consent",
        title="Explains how to withdraw consent, as easily as it was given",
        requirement="How the user can withdraw consent, with the ease of doing so comparable to the ease of giving it.",
        passes_if="It gives a concrete way to withdraw consent (e.g. a setting, link, button or email) that is about as easy as signing up.",
        fails_if="Withdrawal is not mentioned, or only a much harder route is offered (signed letter, post, notarised form, long waiting period), or withdrawal is said to be impossible.",
        cites="Act s.6(4), s.5(1)(ii); Rules r.3(c)(i)",
    ),
    Check(
        id="rights",
        title="Explains the rights to access, correct and erase",
        requirement="How the user can exercise their rights under the Act: a summary of their data (access) and correction, completion, updating and erasure.",
        passes_if="It mentions BOTH access (a summary of the data/processing) AND correction/updating AND erasure, and says how to make the request.",
        fails_if="Access, correction or erasure is missing, or there is no way given to make a request.",
        cites="Act ss.11-12; Rules r.3(c)(ii), r.14(1)",
    ),
    Check(
        id="nomination",
        title="Mentions the right to nominate",
        requirement="That the user may nominate another person to exercise their rights in the event of death or incapacity.",
        passes_if="It says the user can nominate someone to exercise their rights if they die or become unable to.",
        fails_if="Nomination is not mentioned.",
        cites="Act s.14; Rules r.14(4)",
    ),
    Check(
        id="grievance",
        title="Gives a grievance route with a response time of 90 days or less",
        requirement="How to raise a grievance with the business, and the period within which it will respond (the Rules cap this at 90 days).",
        passes_if="It explains how to raise a grievance with the business AND states a response period of 90 days or less.",
        fails_if="No grievance route, no response period, or a period longer than 90 days.",
        cites="Act s.13(1)-(2), s.5(1)(ii); Rules r.14(3)",
    ),
    Check(
        id="board_complaint",
        title="Explains how to complain to the Data Protection Board of India",
        requirement="The manner in which the user may complain to the Data Protection Board of India.",
        passes_if="It names the Data Protection Board (of India) and says the user can complain to it (how or where).",
        fails_if="The Board is not mentioned, or a wrong body is named instead (e.g. 'Data Protection Authority', 'supervisory authority', CERT-In, a consumer court).",
        cites="Act s.5(1)(iii), s.13(3); Rules r.3(c)(iii)",
    ),
    Check(
        id="contact",
        title="Gives contact details of a DPO or a person who can answer questions",
        requirement="Business contact information of the Data Protection Officer, or of a person who can answer questions about the processing.",
        passes_if="It gives an actual contact detail (email, phone or address) for the DPO or a named contact person/office for privacy questions.",
        fails_if="There is no contact detail, or only a vague 'contact us' / 'through our website' with no address, email or phone.",
        cites="Act s.8(9), s.6(3); Rules r.9",
    ),
    Check(
        id="language",
        title="Offers the notice in English or an Indian language",
        requirement="The option to read the notice in English or any language in the Eighth Schedule to the Constitution.",
        passes_if="It tells the user they can read the notice in English or in Indian (Eighth Schedule) languages such as Hindi, and how.",
        fails_if="No language option is mentioned, or it says the notice is available in English only.",
        cites="Act s.5(3)",
    ),
    Check(
        id="no_foreign_law",
        title="Doesn't import foreign-law ideas",
        requirement="No rights, legal bases or regulators that come from other laws (GDPR, CCPA) presented as if they apply under the DPDP Act.",
        passes_if="Nothing from the fails_if list appears. Citing DPDP 'legitimate uses' (s.7) is fine.",
        fails_if="It relies on 'legitimate interest(s)', or offers a 'right to data portability', 'right to object', 'right to restrict processing' or a CCPA-style 'do not sell' opt-out as DPDP rights, or names a 'supervisory authority' / 'Data Protection Authority' as the regulator.",
        cites="Act ss.4, 7, 11-14, 18 (the Act's own grounds, rights and regulator)",
    ),
    Check(
        id="children",
        title="Handles children's data correctly",
        requirement="For users under 18: processing only with verifiable consent of a parent or lawful guardian, and no tracking, behavioural monitoring or targeted advertising directed at children.",
        passes_if="It says data of users under 18 is processed only with verifiable parental/guardian consent, AND says children are not tracked, behaviourally monitored or shown targeted ads.",
        fails_if="The age is wrong (e.g. under 13 or 16), parental consent is missing, or it allows tracking or targeted/personalised ads for children.",
        cites="Act s.2(f), s.9(1), s.9(3); Rules r.10",
        children_only=True,
    ),
)

BY_ID = {c.id: c for c in CHECKS}


def applicable(children: bool) -> list[Check]:
    """Checks that apply to a business. The children check only applies if it has users under 18."""
    return [c for c in CHECKS if children or not c.children_only]
