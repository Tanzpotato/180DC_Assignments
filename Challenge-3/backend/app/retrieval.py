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
            # ✅ Handle JSON array
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    docs = parsed
                else:
                    raise ValueError("Expected a JSON array in corpus file.")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON array in {abs_path}") from e
        else:
            # ✅ Handle JSONL (one JSON object per line)
            for i, line in enumerate(content.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        docs.append(obj)
                    else:
                        docs.append({"id": i, "text": str(obj)})
                except json.JSONDecodeError as e:
                    print(f"⚠️ Skipping invalid JSON at line {i}: {e}")

    if not docs:
        # ✅ Fallback so backend never crashes
        docs.append({
            "id": 0,
            "title": "No Valid Cases",
            "year": "N/A",
            "jurisdiction": "Unknown",
            "tags": ["empty"],
            "text": "⚠️ No valid cases could be loaded from the corpus."
        })

    return docs
