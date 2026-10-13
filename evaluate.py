
import json
from assistant import ask

with open("eval.json", "r", encoding="utf-8") as file:
    tests = json.load(file)

passed = 0

print("QUESTION | EXPECTED | ACTUAL | RESULT")
print("-" * 65)

for test in tests:
    result = ask(test["question"], test["as_of_date"])
    expected = test["expected_status"]
    actual = result["status"]

    if actual == expected:
        passed += 1
        label = "PASS"
    else:
        label = "FAIL"

    print(
        test["question"][:30],
        "|", expected,
        "|", actual,
        "|", label
    )

print("-" * 65)
print("Status score:", passed, "/", len(tests))
