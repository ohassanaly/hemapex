import pandas as pd


def get_max_redcap_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retrieve for each patient (rghc) the latest date in the redcap data
    """
    ## retreive all the date columns in the redcap df
    date_columns = []
    for col in df.columns:
        try:
            pd.to_datetime(df[col], format="%d/%m/%Y", errors="raise")
            date_columns.append(col)
        except Exception as e:
            print(e)

    result = (
        df.groupby("rghc")[date_columns]
        .agg(list)
        .apply(lambda row: [x for lst in row for x in lst if pd.notna(x)], axis=1)
        .apply(lambda lst: pd.to_datetime(lst, format="%d/%m/%Y").max())
        .to_frame(name="max_redcap_date")
    )

    return result.reset_index()


if __name__ == "__main__":
    update_rghc_path = "/home/ohassanaly/work/hemapex/src/data/updated_rghc.pkl"
    tasy_src_path = "/home/ohassanaly/work/hemapex/src/data/latest_tasy.csv"
    redcap_input_path = (
        "/home/ohassanaly/work/hemapex/src/data/mieloma_multiplo_redcap.csv"
    )
    import pickle

    tasy_df = pd.read_csv(tasy_src_path)  # .drop_duplicates(subset = "rghc")
    red_df = pd.read_csv(redcap_input_path, sep=";")
    red_df.rename(columns={"RGHC": "rghc"}, inplace=True)

    date_df = get_max_redcap_date(red_df).merge(tasy_df[["rghc", "data_dt"]], on="rghc")
    date_df["data_dt"] = pd.to_datetime(
        date_df["data_dt"], format="%Y-%m-%d", errors="raise"
    )
    date_df["dt_diff"] = (date_df["data_dt"] - date_df["max_redcap_date"]).dt.days

    update_rghc_list = date_df[date_df["dt_diff"] < 30].rghc.to_list()
    # 6 meses é o periodo do seguimento anterior
    # 1 mes para estar seguro que não vou ter grandes diferencias

    with open(update_rghc_path, "wb") as file:
        pickle.dump(update_rghc_list, file)
