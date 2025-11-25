from api_calls import Provider, MODELS, call_llm_structured
from pathlib import Path

test_mode = False
erase_mode = False
n_test = 2
tasy_src_path = Path(".") / "src/data/latest_tasy.csv"
# redcap_src_path = Path(".") / "src/data/redcap_treatment_labels.csv"
update_rghc_path = Path(".") / "src/data/updated_rghc.pkl"

provider = Provider.GEMINI
model = MODELS[provider]
single_dir = Path(".") / f"src/results/{provider.value}_rghc/"
global_dir = Path(".") / f"src/results/{provider.value}_full_result/"

single_dir.mkdir(parents=True, exist_ok=True)
global_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    from structured_treatment import TreatmentLines
    from datetime import datetime

    from dotenv import load_dotenv
    import pandas as pd
    from tqdm import tqdm

    import logging
    import pickle

    load_dotenv()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = Path(".") / f"src/logs/log_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_path,
        filemode="a",
    )

    load_dotenv()

    with open(update_rghc_path, "rb") as file:
        update_rghc_list = pickle.load(file)
    text_df = pd.read_csv(tasy_src_path)
    # label_df = pd.read_csv(redcap_src_path)

    if test_mode:
        api_df = text_df[text_df.rghc.isin(update_rghc_list)].iloc[:n_test][
            ["rghc", "text"]
        ]
        # api_df = text_df[text_df.rghc.isin(label_df.rghc.tolist())].iloc[:n_test][
        #     ["rghc", "text"]
        # ]
        logging.info(f"Extracting treatments for {api_df.rghc.nunique()} rghc")
    else:
        api_df = text_df[text_df.rghc.isin(update_rghc_list)][["rghc", "text"]]
        # api_df = text_df[text_df.rghc.isin(label_df.rghc.tolist())][["rghc", "text"]]
        logging.info(f"Extracting treatments for {api_df.rghc.nunique()} rghc")

    df = pd.DataFrame()

    for index, row in tqdm(api_df.iterrows()):
        rghc = row["rghc"]
        logging.info(f"Processing rghc : {rghc}")
        single_output_path = single_dir / f"{rghc}.csv"
        # check if the patient was already processed
        if not erase_mode and single_output_path.exists():
            logging.info(f"Patient {rghc} already processed")
            continue

        else:
            result = call_llm_structured(
                provider=provider,
                model=model,
                instruction=open(Path(".") / "src/txt/instructions.txt").read(),
                unstructured_text=row["text"],
                schema_model=TreatmentLines,
            )

            try:
                data = result.model_dump()
            except Exception as e:
                print(f"Failed to save response for {provider.value}: {e}")

            try:
                df1 = pd.DataFrame(data["linhas"])
                df1["rghc"] = rghc
                # save results one by one for safety
                df1.to_csv(Path(single_output_path), index=False)
                logging.info(f"Response for {rghc} saved to {single_output_path}")
                df = pd.concat([df, df1])
            except Exception as e:
                logging.error(e)

    # final save
    try:
        global_output_path = (
            global_dir / f"{api_df.rghc.nunique()}_rghc_{timestamp}.csv"
        )
        df.to_csv(global_output_path, index=False)
        logging.info(f"Full extraction saved to {global_output_path}")
    except Exception as e:
        logging.error(e)
