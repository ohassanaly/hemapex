import pandas as pd
from config import tasy_tratamento_columns


def latest_tasy(
    input_path: str, output_path: str, text_columns=tasy_tratamento_columns
) -> None:
    """
    Input : the scrapping result of registro.tasy
    retrieve the latest consultation for each patient, with the "text" column containing the relevant text
    export the result as a csv
    """
    source_df = pd.read_csv(input_path, low_memory=False)
    source_df["data_dt"] = pd.to_datetime(source_df.data, format="%d/%m/%Y")
    source_df[text_columns] = (
        source_df[text_columns].astype(str).fillna("").replace("nan", "", regex=False)
    )
    # keep the latest consultation for each patient
    df = source_df.sort_values(by=["data_dt"], ascending=False).drop_duplicates(
        subset=["rghc"]
    )
    # concatenate the relevant sections into one single text
    df["text"] = df[text_columns].apply(lambda row: " ".join(row.values), axis=1)
    # add a person_id for deidentification
    df["person_id"] = df.index
    df[["rghc", "person_id", "data", "data_dt", "text"] + text_columns].to_csv(
        output_path, index=False
    )
    return


if __name__ == "__main__":
    from pathlib import Path

    latest_tasy(
        Path(".") / "src/data/tmo_tasy.csv",
        Path(".") / "src/data/tasy_api.csv",
        tasy_tratamento_columns,
    )
    tdf = pd.read_csv(Path(".") / "src/data/tasy_api.csv")
    rdf = pd.read_csv(Path(".") / "src/data/tmo_redcap.csv")
    # keep only patients with a single transplant recorded
    tdf[tdf.rghc.isin(rdf.rghc.tolist())].to_csv(Path(".") / "src/data/tasy_api.csv")
