import re

def split_into_bubbles(text: str, max_parts: int = 3) -> list[str]:
    """
    Splits a reply into natural chat-bubble-sized chunks.
    Splits on sentence boundaries, then merges short fragments
    so bubbles feel balanced, not choppy.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s]

    if len(sentences) <= 1:
        return [text.strip()]

    # Merge sentences into at most max_parts groups
    if len(sentences) <= max_parts:
        return sentences

    groups = [[] for _ in range(max_parts)]
    for i, sentence in enumerate(sentences):
        groups[i % max_parts].append(sentence)

    return [" ".join(g).strip() for g in groups if g]