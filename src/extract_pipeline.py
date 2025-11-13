test_mode = True
n_test = 10
tasy_src_path = "src/data/latest_tasy.csv"
redcap_src_path = "src/data/redcap_treatment_labels.csv"

if __name__ == "__main__":
    import os
    import openai
    from dotenv import load_dotenv
    from extract_treatments import extract_treatment_lines
    import pandas as pd
    from tqdm import tqdm
    import logging
    from datetime import datetime

    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = f"src/logs/log_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_path,
        filemode="a",
    )

    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    text_df = pd.read_csv(tasy_src_path)
    label_df = pd.read_csv(redcap_src_path)

    if test_mode:
        api_df = text_df[text_df.rghc.isin(label_df.rghc.tolist())].iloc[:n_test][
            ["rghc", "text"]
        ]
        logging.info(f"Extracting treatments for {api_df.rghc.nunique()}")
    else:
        api_df = text_df[text_df.rghc.isin(label_df.rghc.tolist())][["rghc", "text"]]
        logging.info(f"Extracting treatments for {api_df.rghc.nunique()}")

    df = pd.DataFrame()

    for index, row in tqdm(api_df.iterrows()):
        rghc = row["rghc"]
        logging.info(f"Processing rghc : {rghc}")

        treatment_lines = extract_treatment_lines(client, row["text"])

        try:
            data = treatment_lines.model_dump()
        except AttributeError:
            data = treatment_lines.__dict__

        output_path = f"src/results/{rghc}.csv"
        try:
            df1 = pd.DataFrame(data["linhas"])
            df1["rghc"] = rghc
            # save results one by one for safety
            df1.to_csv(output_path, index=False)
            logging.info(f"Response for {rghc} saved to {output_path}")
            df = pd.concat([df, df1])
        except Exception as e:
            logging.error(e)

    # final save
    try:
        output_path = f"src/results/full_result_{timestamp}.csv"
        df.to_csv(output_path, index=False)
        logging.info(f"Full extraction saved to {output_path}")
    except Exception as e:
        logging.error(e)
