import re
import pandas as pd
from rapidfuzz import fuzz
from typing import List, Dict, Any


def normalize_text(text: Any) -> str:
    """Lowercase, strip, remove special chars, collapse whitespace."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_blocking_key(row: pd.Series, fields: List[str]) -> str:
    """First 3 chars of each mapped field concatenated."""
    parts = []
    for f in fields:
        val = str(row.get(f, ""))[:3]
        parts.append(val)
    return "".join(parts)


def run_matching(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    id1: str,
    id2: str,
    field_pairs: List[Dict[str, str]],
    same_source: bool,
) -> List[Dict[str, Any]]:
    """
    Main matching function.
    field_pairs: list of {col1, col2}
    Returns list of {id1_val, fields1_vals, id2_val, fields2_vals, match_score}
    """
    cols1 = [fp["col1"] for fp in field_pairs]
    cols2 = [fp["col2"] for fp in field_pairs]

    # Work on copies with normalized fields
    df1 = df1.copy()
    df2 = df2.copy()

    norm_cols1 = {}
    norm_cols2 = {}
    for fp in field_pairs:
        c1 = fp["col1"]
        c2 = fp["col2"]
        norm_c1 = f"__norm_{c1}"
        norm_c2 = f"__norm_{c2}"
        df1[norm_c1] = df1[c1].apply(normalize_text)
        df2[norm_c2] = df2[c2].apply(normalize_text)
        norm_cols1[c1] = norm_c1
        norm_cols2[c2] = norm_c2

    # Build blocking keys
    block_fields1 = [norm_cols1[c] for c in cols1]
    block_fields2 = [norm_cols2[c] for c in cols2]

    df1["__block_key"] = df1.apply(lambda r: build_blocking_key(r, block_fields1), axis=1)
    df2["__block_key"] = df2.apply(lambda r: build_blocking_key(r, block_fields2), axis=1)

    results = []

    # Group by blocking key
    blocks1 = df1.groupby("__block_key")
    blocks2 = df2.groupby("__block_key")

    common_keys = set(blocks1.groups.keys()) & set(blocks2.groups.keys())

    for key in common_keys:
        group1 = blocks1.get_group(key)
        group2 = blocks2.get_group(key)

        for _, row1 in group1.iterrows():
            for _, row2 in group2.iterrows():
                id1_val = str(row1[id1])
                id2_val = str(row2[id2])

                # Self-comparison: skip self-matches, keep only one direction
                if same_source:
                    if id1_val == id2_val:
                        continue
                    if id1_val > id2_val:
                        continue

                # Compute scores for each field pair
                scores = []
                for fp in field_pairs:
                    c1 = fp["col1"]
                    c2 = fp["col2"]
                    v1 = str(row1.get(norm_cols1[c1], ""))
                    v2 = str(row2.get(norm_cols2[c2], ""))
                    score = fuzz.token_sort_ratio(v1, v2)
                    scores.append(score)

                if not scores:
                    continue

                match_score = sum(scores) / len(scores)

                if match_score < 50:
                    continue

                fields1_vals = {c: str(row1.get(c, "")) for c in cols1}
                fields2_vals = {c: str(row2.get(c, "")) for c in cols2}

                results.append({
                    "id1_val": id1_val,
                    "fields1_vals": fields1_vals,
                    "id2_val": id2_val,
                    "fields2_vals": fields2_vals,
                    "match_score": round(match_score, 2),
                })

    return results
