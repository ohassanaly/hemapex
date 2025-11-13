"""
Compare the results between the treatments extracted from text using the API
and the ground truth labels from the REDCAP database
"""

if __name__ == "__main__":
    import pandas as pd
    from utils import post_process_drugs
    from config import label_cols

    api_df = pd.read_csv(
        "/home/ohassanaly/work/hemapex/src/results/full_result_2025-11-13_16-59-43.csv"
    )[label_cols]
    api_df.inducao_medicamentos.apply(lambda x: post_process_drugs(x))

    check_df = pd.read_csv("/home/ohassanaly/work/hemapex/src/data/df_12_11_2025.csv")
    check_df = check_df[check_df.rghc.isin(api_df.rghc.tolist())][label_cols]

    # I might want to upload
    diff_mask = api_df != check_df

    num_diff = diff_mask.sum().sum()
    num_total = diff_mask.size

    ratio = num_diff / num_total
    print(ratio)

    api_df.compare(check_df).to_csv("src/results/compared.csv", index=False)
