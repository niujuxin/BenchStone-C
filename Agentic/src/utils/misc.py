import json
from pathlib import Path
from typing import Dict, List


def read_jsonl(fp: str | Path) -> List[Dict]:
    lines = Path(fp).read_text().splitlines()
    return [json.loads(line) for line in lines]


def read_json(fp: str | Path) -> Dict:
    with open(fp, 'r') as f:
        return json.load(f)


def dump_json(data: Dict, fp: str | Path) -> None:
    with open(fp, 'w') as f:
        json.dump(data, f, indent=2)
