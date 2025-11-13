"""
Compare the results between the treatments extracted from text using the API
and the ground truth labels from the REDCAP database

Several levels of checks :
Number of therapy lines
Drugs match for each therapy
Dates distance
"""

import pandas as pd


def compare_number_lines(
    df1: pd.DataFrame, df2: pd.DataFrame, id_col: str = "rghc"
) -> pd.Series:
    return abs(
        df1.groupby(id_col)[id_col].count() - df2.groupby(id_col)[id_col].count()
    )


if __name__ == "__main__":
    from utils import post_process_drugs, sort_drugs
    from config import label_cols, drugs_ref

    api_df = pd.read_csv(
        "/home/ohassanaly/work/hemapex/src/results/full_result_2025-11-13_16-59-43.csv"
    )[label_cols]
    check_df = pd.read_csv("/home/ohassanaly/work/hemapex/src/data/df_12_11_2025.csv")
    check_df = check_df[check_df.rghc.isin(api_df.rghc.tolist())][label_cols]

    ### preprocessing
    cols = [
        "inducao_medicamentos",
        "consolidacao_medicamentos",
        "manutencao_medicamentos",
    ]

    api_df[cols] = api_df[cols].apply(
        lambda col: col.apply(post_process_drugs, args=(drugs_ref,))
    )

    api_df[cols] = api_df[cols].apply(lambda col: col.apply(sort_drugs))
    check_df[cols] = check_df[cols].apply(lambda col: col.apply(sort_drugs))

    ### end of preprocessing

    # Compare the number of lines
    a = compare_number_lines(api_df, check_df)
    print(
        "the LLM did not find the same number of lines than REDCAP in",
        len(a[a != 0]),
        "cases among the",
        len(a),
        "cases evaluated",
    )

    # Compare the found drugs

    # Compare the dates
