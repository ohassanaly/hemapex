import pandas as pd


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
