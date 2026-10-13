
- Used plain Python so the assistant runs offline without an API key.
- Used explicit rules for the known policy questions rather than generating unsupported answers.
- Treated the August amendment as overriding earlier master-policy clauses where it explicitly replaces or deletes them.
- Used 1 September 2026 as the effective date for the refund amendment.
- Used Decimal for MDR and GST calculations to avoid floating-point money errors.
- Return CANNOT_ANSWER for questions that the current rules do not support.
- Limitation: question matching is based on keywords and does not cover every possible wording.