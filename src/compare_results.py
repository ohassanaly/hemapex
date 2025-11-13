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
    return True if the dates "agree"
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
                pd.to_datetime(d1, format="%d/%m/%Y").year
                == pd.to_datetime(d2, format="%d/%m/%Y").year
            ) and (
                pd.to_datetime(d1, format="%d/%m/%Y").month
                == pd.to_datetime(d2, format="%d/%m/%Y").month
            ):
                return True
            else:
                return False


def compare_str(s1, s2):
    """
    return True if the string are the same
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

    api_result_path = (
        "/home/ohassanaly/work/hemapex/src/results/full_result_2025-11-13_20-30-36.csv"
    )
    check_label_path = "/home/ohassanaly/work/hemapex/src/data/df_12_11_2025.csv"

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
    df1 = api_df[~api_df.rghc.isin(diff_id)].copy().reset_index(drop=True)
    df2 = check_df[~check_df.rghc.isin(diff_id)].copy().reset_index(drop=True)
    agreement, comparison = compare_df(df1, df2)
    print("number of cells where the two methods agree :", agreement)
    print("number of comparisons evaluated:", comparison)
    print("agreement ratio: ", round(agreement / comparison, 2) * 100, "%")
