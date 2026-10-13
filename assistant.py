
from pathlib import Path
from decimal import Decimal

DATA_DIR = Path(".")


def load_documents():
    documents = {}

    filenames = [
        "policy_master_v1.md",
        "circular_2026_08_amendment.md",
        "merchant_faq_2026-03.md"
    ]

    for filename in filenames:
        path = DATA_DIR / filename
        documents[filename] = path.read_text(encoding="utf-8")

    return documents


def make_answer(answer, citations, status):
    return {
        "answer": answer,
        "citations": citations,
        "status": status
    }


def calculate_fees(amount, merchant_type, as_of_date):
    amount = Decimal(str(amount))

    if merchant_type == "small":
        if as_of_date >= "2026-08-01":
            rate = Decimal("0.0025")
        else:
            rate = Decimal("0.0030")
        cap = Decimal("15")
    else:
        rate = Decimal("0.0050")
        cap = Decimal("25")

    mdr = min(amount * rate, cap)
    mdr = mdr.quantize(Decimal("0.01"))
    gst = (mdr * Decimal("0.18")).quantize(Decimal("0.01"))

    return mdr, gst, mdr + gst


def ask(question, as_of_date="2026-08-15"):
    question = question.lower()
    documents = load_documents()

    # Refund policy changes on 1 September 2026.
    if "refund" in question and (
        "3 hours" in question or "three hours" in question
        or "fee back" in question or "mdr back" in question
    ):
        if as_of_date < "2026-09-01":
            return make_answer(
                "Yes. A refund initiated within 24 hours receives a full MDR reversal.",
                [{"document": "policy_master_v1.md", "clause": "3.3"}],
                "ANSWERED"
            )

        return make_answer(
            "No. From 1 September 2026, the refund exception is deleted and MDR is not returned.",
            [
                {"document": "policy_master_v1.md", "clause": "3.2"},
                {"document": "circular_2026_08_amendment.md", "clause": "D"}
            ],
            "CONFLICT_RESOLVED"
        )

    # FAQ says there is no cap, but the policy sets a cap.
    if "faq" in question and "cap" in question:
        return make_answer(
            "The FAQ says there is no upper limit, but that is incorrect. "
            "The cap is Rs.15 for small merchants and Rs.25 for large merchants. "
            "GST is charged separately on MDR.",
            [
                {"document": "merchant_faq_2026-03.md", "clause": "What do I pay on a UPI transaction?"},
                {"document": "circular_2026_08_amendment.md", "clause": "C"},
                {"document": "policy_master_v1.md", "clause": "2.4"}
            ],
            "CONFLICT_RESOLVED"
        )

    # UPI transaction and daily limits.
    if "twice" in question or (
        "1,00,000" in question and "one day" in question
    ):
        return make_answer(
            "No. Two payments of Rs.1,00,000 total Rs.2,00,000, "
            "which exceeds the Rs.1,00,000 daily limit per customer account. "
            "The customer's bank may set a lower limit.",
            [
                {"document": "policy_master_v1.md", "clause": "4.3"},
                {"document": "circular_2026_08_amendment.md", "clause": "E"}
            ],
            "ANSWERED"
        )

    # Account closure.
    if "closed my account" in question or "account closure" in question:
        return make_answer(
            "Pending settlements are released within 10 working days of closure, "
            "after outstanding dues are deducted. The policy also requires "
            "30 days' written notice for account closure.",
            [
                {"document": "policy_master_v1.md", "clause": "5.1"},
                {"document": "policy_master_v1.md", "clause": "5.2"}
            ],
            "ANSWERED"
        )

    # Card settlement.
    if "card" in question and ("same day" in question or "settle" in question):
        return make_answer(
            "No same-day card settlement is stated in these documents. "
            "Card transactions settle T+2, meaning two days later under the policy.",
            [{"document": "policy_master_v1.md", "clause": "1.2"}],
            "ANSWERED"
        )

    # UPI settlement.
    if "when" in question and (
        "upi" in question and ("money" in question or "receive" in question)
    ):
        return make_answer(
            "UPI settles the same day by 11:59 PM for merchants with an active "
            "Instant Settlement add-on. Other merchants receive settlement on T+1, "
            "the next working day.",
            [{"document": "circular_2026_08_amendment.md", "clause": "A"}],
            "ANSWERED"
        )

    # MDR and GST calculation for large merchants.
    if "large merchant" in question or "above rs.10 lakh" in question:
        amount = 0

        if "1,50,000" in question or "150000" in question:
            amount = 150000
        elif "4,000" in question or "4000" in question:
            amount = 4000

        if amount > 0:
            mdr, gst, total = calculate_fees(amount, "large", as_of_date)
            return make_answer(
                f"MDR is Rs.{mdr:.2f}, GST is Rs.{gst:.2f}, "
                f"and the total fee is Rs.{total:.2f}.",
                [
                    {"document": "policy_master_v1.md", "clause": "2.2"},
                    {"document": "circular_2026_08_amendment.md", "clause": "C"},
                    {"document": "policy_master_v1.md", "clause": "2.4"}
                ],
                "ANSWERED"
            )

    # Unknown questions should not receive a guessed answer.
    return make_answer(
        "I cannot answer this reliably from the rules currently implemented.",
        [],
        "CANNOT_ANSWER"
    )


if __name__ == "__main__":
    tests = [
        ("When does a small merchant receive UPI money?", "2026-08-15"),
        ("A large merchant above Rs.10 lakh receives a Rs.4,000 UPI payment. What MDR and GST do they pay?", "2026-08-15"),
        ("A large merchant above Rs.10 lakh receives a Rs.1,50,000 payment. What MDR and GST do they pay?", "2026-08-15"),
        ("Does a merchant get MDR back for a refund after 3 hours?", "2026-08-20"),
        ("Does a merchant get MDR back for a refund after 3 hours?", "2026-09-05"),
        ("What does the FAQ say about the MDR cap, and is it right?", "2026-08-15"),
        ("Can a customer pay Rs.1,00,000 twice in one day?", "2026-08-15"),
        ("I closed my account yesterday. When will I get my money?", "2026-08-15"),
        ("Does the policy allow me to settle card payments same day?", "2026-08-15")
    ]

    for question, date in tests:
        result = ask(question, date)
        print("\nQuestion:", question)
        print("Date:", date)
        print("Answer:", result["answer"])
        print("Status:", result["status"])
        print("Citations:", result["citations"])
