import pandas as pd
from config import (
    src_drug_cols_dict,
    final_drug_cols_dict,
    rename_columns_dict,
    label_cols,
)
from utils import retrieve_drugs


def redcap_labels(redcap_input_path: str, label_output_path: str) -> None:
    """
    Retrieve the relevant treatment labels from REDCAP database to evaluate the results of API calls
    """
    redcap_df = pd.read_csv(redcap_input_path, sep=";", low_memory=False)

    redcap_df.rename(columns={"RGHC": "rghc"}, inplace=True)
    # recasting check formular data
    redcap_df.replace({"Checked": True, "Unchecked": False}, inplace=True)

    # adding rghc to treatment lines
    rghc = ""  # variable initialization
    for index, row in redcap_df.iterrows():
        if row["Repeat Instrument"] == "Linha de Tratamento":
            redcap_df.at[index, "rghc"] = rghc
        else:
            rghc = row["rghc"]

    redcap_df = retrieve_drugs(
        redcap_df, src_drug_cols_dict["inducao"], final_drug_cols_dict["inducao"]
    )
    redcap_df = retrieve_drugs(
        redcap_df,
        src_drug_cols_dict["consolidacao"],
        final_drug_cols_dict["consolidacao"],
    )
    redcap_df = retrieve_drugs(
        redcap_df, src_drug_cols_dict["manutencao"], final_drug_cols_dict["manutencao"]
    )

    redcap_df.rename(columns=rename_columns_dict, inplace=True)

    # excluding unactualized patients
    df1 = redcap_df.dropna(subset=["Sexo"])
    unactualized_patients = df1[df1["Desfecho final do paciente"].isna()][
        "rghc"
    ].tolist()
    redcap_df = redcap_df[~redcap_df.rghc.isin(unactualized_patients)]

    # keep only treatment lines
    redcap_df = redcap_df[redcap_df["Repeat Instrument"] == "Linha de Tratamento"]

    redcap_df[label_cols].to_csv(label_output_path, index=False)

    return


if __name__ == "__main__":
    redcap_labels(
        redcap_input_path="src/data/mieloma_multiplo_redcap.csv",
        label_output_path="src/data/redcap_treatment_labels.csv",
    )
