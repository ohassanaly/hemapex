"""
Compare the results between the treatments extracted from text using the API
and the ground truth labels from the REDCAP database

Several levels of checks :
Number of treatment lines
Steps of the line
Drugs match for each care
Dates match (distance?) for each care
"""

import pandas as pd
from typing import List
from config import date_col_list, str_col_list
from utils import sort_drugs


def compare_number_lines(
    df1: pd.DataFrame, df2: pd.DataFrame, id_col: str = "rghc"
) -> pd.Series:
    """
    the first step is to check if both methods identified the same number of oncological treatment lines
    """
    return abs(
        df1.groupby(id_col)[id_col].count() - df2.groupby(id_col)[id_col].count()
    )


def compare_date(d1, d2) -> bool:
    """
    return True if the dates differ are within a 30 days interval
    False if they are different
    """

    if pd.isna(d1):
        if pd.isna(d2):
            return True
        else:
            return False
    else:
        if pd.isna(d2):
            return False
        else:
            if (
                abs(
                    (
                        pd.to_datetime(d1, format="%d/%m/%Y")
                        - pd.to_datetime(d2, format="%d/%m/%Y")
                    ).days
                )
                <= 30
            ):
                return True
            else:
                return False


def compare_str(s1, s2):
    """
    return True if the lowercased strings are exactly the same
    False if they are different
    """

    if pd.isna(s1):
        if pd.isna(s2):
            return True
        else:
            return False
    else:
        if pd.isna(s2):
            return False
        else:
            if sort_drugs(s1.lower()) == sort_drugs(s2.lower()):
                return True
            else:
                return False


def compare_df(df1: pd.DataFrame, df2: pd.DataFrame) -> List[int]:
    """
    count the number of agreements and number of comparisons
    """
    agreements = 0
    comparisons = 0

    for index, row in df1.iterrows():
        for item in row.items():
            variable = item[0]
            if variable in date_col_list:
                if compare_date(item[1], df2.at[index, variable]):
                    agreements += 1
                comparisons += 1

            elif variable in str_col_list:
                if compare_str(item[1], df1.at[index, variable]):
                    agreements += 1
                comparisons += 1
            else:  # rghc or line number
                pass
    return (agreements, comparisons)


if __name__ == "__main__":
    from utils import post_process_drugs, sort_drugs
    from config import label_cols, drugs_ref
    import pickle

    api_result_path = (
        "/home/ohassanaly/work/hemapex/src/results/final_result_1411_303_rghc.csv"
    )
    check_label_path = "/home/ohassanaly/work/hemapex/src/data/df_12_11_2025.csv"
    individual_compare_path = (
        "/home/ohassanaly/work/hemapex/src/results/testing/individual_compare.csv"
    )

    update_rghc_path = "/home/ohassanaly/work/hemapex/src/data/updated_rghc.pkl"

    # data loading
    api_df = pd.read_csv(api_result_path)[label_cols]
    check_df = pd.read_csv(check_label_path)
    check_df = check_df[check_df.rghc.isin(api_df.rghc.tolist())][label_cols]
    # end of data loading

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

    # only keep up to date patients
    with open(update_rghc_path, "rb") as file:
        update_rghc_list = pickle.load(file)
    api_df = api_df[api_df.rghc.isin(update_rghc_list)]
    check_df = check_df[check_df.rghc.isin(update_rghc_list)]

    print("number of rghc used for final evaluation", api_df.rghc.nunique())

    ### end of preprocessing

    ### Comparisons
    # Compare the number of lines
    line_compare = compare_number_lines(api_df, check_df)
    diff_id = line_compare[line_compare != 0].index.tolist()
    print(
        "the two methods disagree on the number of line for",
        len(diff_id),
        "cases among the",
        len(line_compare),
        "cases evaluated",
    )

    # Comparison cell by cell when agreement on the number of lines
    df1 = (
        api_df[~api_df.rghc.isin(diff_id)]
        .copy()
        .sort_values(by=["rghc", "line_number"])
        .reset_index(drop=True)
    )
    df2 = (
        check_df[~check_df.rghc.isin(diff_id)]
        .copy()
        .sort_values(by=["rghc", "line_number"])
        .reset_index(drop=True)
    )

    df1.compare(
        df2,
        keep_shape=True,
        # keep_equal=True,
        result_names=("api", "redcap"),
    ).to_csv(individual_compare_path, index=False)

    print(
        "number of rghc where the following comparisons are evaluated :",
        df1.rghc.nunique(),
    )
    agreement, comparison = compare_df(df1, df2)
    print("number of cells where the two methods agree :", agreement)
    print("number of comparisons evaluated:", comparison)
    print("agreement ratio: ", round(agreement / comparison, 2) * 100, "%")
