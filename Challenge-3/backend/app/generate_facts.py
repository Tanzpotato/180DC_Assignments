import json
import os

INPUT_FILE = "Metadata/cases.jsonl"
OUTPUT_FILE = "backend/app/facts.py"

def expand_case_to_facts(case: dict, idx: int, per_case: int = 10) -> list:
    facts = []
    title = case.get("title", f"Case {idx}")
    text = case.get("text", "")
    year = case.get("year", "Unknown Year")
    jurisdiction = case.get("jurisdiction", "Unknown Jurisdiction")

    facts.append(f"{title} was decided in {jurisdiction} in {year}.")
    facts.append(f"The case is commonly referred to as {title}.")
    facts.append(f"Jurisdiction of this case was {jurisdiction}.")
    facts.append(f"The dispute arose around {text[:80]}...")

    words = text.split()
    for i in range(1, per_case - 4):  # already added 4
        snippet = " ".join(words[i*10:(i+1)*10]) or f"Detail {i} not specified."
        facts.append(f"In {title}, evidence showed that {snippet.strip()}.")

    return facts


def generate_facts(input_file: str, output_file: str, per_case: int = 10):
    all_facts = []
    with open(input_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            try:
                case = json.loads(line)
                facts = expand_case_to_facts(case, idx, per_case=per_case)
                all_facts.extend(facts)
            except json.JSONDecodeError:
                print(f"⚠️ Skipping invalid JSON line {idx}")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# Auto-generated facts file\n")
        out.write("DEFAULT_FACTS = [\n")
        for fact in all_facts:
            out.write(f'    "{fact}",\n')
        out.write("]\n")

    print(f"✅ Generated {len(all_facts)} facts into {output_file}")


if __name__ == "__main__":
    os.makedirs("backend/app", exist_ok=True)
    generate_facts(INPUT_FILE, OUTPUT_FILE, per_case=10)
