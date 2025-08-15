# vectormancer/quiz.py
from __future__ import annotations
import random, re
from typing import List, Dict
from .indexer.embedder import embed_texts

# Tiny stopword set (enough for cloze questions without extra deps)
# would prolly connect to an LLM here at some point (from CLI?)
_STOP = {
    "the","a","an","and","or","but","if","then","else","on","in","at","to","for",
    "from","with","of","by","is","are","was","were","be","been","being",
    "as","that","this","these","those","it","its","into","about","over","under",
    "no","not","than","so","such","can","may","might","should","would","will",
    "i","you","we","they","he","she","them","him","her","our","your","their"
}

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')

def _pick_target_word(sentence: str) -> str | None:
    # choose a “content” word: long-ish, not stopword, alphanumeric
    words = re.findall(r"[A-Za-z][A-Za-z\-']+", sentence)
    words = [w for w in words if w.lower() not in _STOP and len(w) >= 4]
    if not words:
        return None
    # prefer rarer-looking words (longer first)
    words.sort(key=lambda w: (-len(w), w.lower()))
    return words[0]

def _sentence_pool(text: str) -> list[str]:
    sents = _SENT_SPLIT.split(text)
    # keep non-trivial sentences
    return [s.strip() for s in sents if len(s.strip()) >= 40]

def generate_quiz(vm, topic: str, num: int = 5, window: int = 800, seed: int = 42) -> List[Dict]:
    """
    Returns a list of {question, answer, path, context} built from top hits for the topic.
    """
    random.seed(seed)

    # retrieve a bunch of candidates
    qvec = embed_texts([topic])[0]
    hits = vm.store.search(qvec, top_k=max(num * 4, 8))
    items: List[Dict] = []

    for h in hits:
        doc = vm.store.get_doc_text(h["path"]) or h.get("text","")
        context = doc
        if doc and "start" in h and "end" in h:
            center = (h["start"] + h["end"]) // 2
            half = window // 2
            s = max(0, center - half)
            e = min(len(doc), center + half)
            context = doc[s:e]

        for sent in _sentence_pool(context):
            tgt = _pick_target_word(sent)
            if not tgt:
                continue
            # build cloze
            blank = "_" * min(10, max(5, len(tgt)))
            q = sent.replace(tgt, blank, 1)
            items.append({
                "question": q,
                "answer": tgt,
                "path": h["path"],
                "context": context
            })
            if len(items) >= num:
                return items

    # fallback: if not enough, pad with whole-chunk questions 
    for h in hits:
        if len(items) >= num:
            break
        snippet = (h.get("text","") or "").strip()
        if not snippet:
            continue
        items.append({
            "question": f"(Context) {snippet[:200]}\nFill the missing key term related to: {topic}\nAnswer: ______",
            "answer": topic.split()[0],
            "path": h["path"],
            "context": snippet
        })
    return items
