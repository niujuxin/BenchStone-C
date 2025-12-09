
import re
from typing import List, Dict

from langchain_core.messages import AIMessage

def extract_fenced_code_blocks(markdown: str) -> List[Dict[str, str]]:
    """
    Extract every fenced-code-block that appears in a Markdown string.

    What is returned?
        A list[dict] where every dict has the keys
            • "code"      – the raw code that was inside the block
            • "language"  – whatever language label (e.g. "python") followed the
                        opening fence, or "" if none was given
            • "fence"     – the exact fence that was used (``` or ~~~, possibly
                        more than three characters)

    How does it work?
        1. A single *verbose* regular-expression scans the whole document at once.
        2. It recognises both back-tick and tilde fences, as long as they are at
        least three characters long, exactly as CommonMark specifies.
        3. The pattern is multi-line (“^” and “$” apply to each line) and
        dot-matches-newline so that we can let “.*?” consume the block’s
        interior lazily.
    """

    _FENCED_BLOCK_RE = re.compile(
        r"""^
            (?P<fence>`{3,}|~{3,})        # opening fence of back-ticks or tildes
            [ \t]*                        # optional spaces
            (?P<lang>[^\n]*)\n            # optional language info up to EOL
            (?P<code>.*?)                 # lazily grab everything inside
            ^(?P=fence)[ \t]*$            # closing fence, same char sequence
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    blocks: List[Dict[str, str]] = []
    for m in _FENCED_BLOCK_RE.finditer(markdown):
        blocks.append(
            {
                "code": m.group("code"),
                "language": m.group("lang").strip(),
                "fence": m.group("fence"),
            }
        )
    return blocks


def retrieve_code_from_markdown(md: str) -> str | None:
    code_blocks = extract_fenced_code_blocks(md)
    if not code_blocks:
        return None
    code = "\n\n".join([cb['code'] for cb in code_blocks])
    return code
