import pandas as pd
from config import drugs_ref
from typing import List
import re


def retrieve_drugs(
    df: pd.DataFrame, src_drug_col: str, target_drug_col: str
) -> pd.DataFrame:
    drug_cols = [c for c in df.columns if c.startswith(src_drug_col)]
    df[drug_cols] = (
        df[drug_cols].fillna(False).astype(bool)
    )  # reversing fillna and astype generates error

    df[target_drug_col] = df[drug_cols].apply(
        lambda row: [
            col.split("(choice=")[1].rstrip(")") for col in drug_cols if row[col]
        ],
        axis=1,
    )
    ##comma-separated string instead of a list:
    df[target_drug_col] = df[target_drug_col].apply(lambda x: ", ".join(x))
    return df


def post_process_drugs(api_text: str, drug_list: List[str] = drugs_ref) -> str:
    if pd.isna(api_text):
        return None
    drugs = [d.strip() for d in re.split(r"[(),]", api_text) if d.strip()]
    filtered = [d for d in drugs if d in drug_list]
    return ", ".join(filtered) if filtered else None


def sort_drugs(s: str) -> str:
    if not isinstance(s, str):
        return None
    return ", ".join(sorted((d.strip() for d in s.split(",")), key=str.lower))
