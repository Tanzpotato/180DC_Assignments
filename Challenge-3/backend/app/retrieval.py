import os, json

def load_corpus(path="Metadata/cases.jsonl"):
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Corpus file not found: {abs_path}")

    docs = []
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        if not content:
            raise ValueError(f"Corpus file is empty: {abs_path}")

        if content.startswith("["):
            # JSON array
            docs = json.loads(content)
        else:
            # JSONL
            for line in content.splitlines():
                line = line.strip()
                if not line:   # ✅ skip blank lines
                    continue
                try:
                    docs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in {abs_path} at line: {line}") from e

    return docs
