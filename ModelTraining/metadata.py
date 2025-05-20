"""
Creates metadata for later code annotation.

This extracts lower & upper quantiles and creates a file
used in later stages.

"""

from collections import OrderedDict
from typing import Dict, List
import pandas as pd
import numpy as np
import os


def process_files(
        folder_path: str,
        language_exts: str,
        quantile_lower: float,
        quantile_upper: float,
        quantile_step: float
        ) -> List[Dict[str, str | float]]:
    """
    Iterates through the files and extracts CPU performance statistics
    for each code extract.

    Args:
        folder_path (str): The path of the metadata directory.
        language_exts (str): File extensions to search for within CSVs.
        quantile_lower (float): The inclusive lower quanitile.
        quantile_upper (float): The exclusive upper quantile.
        quantile_step (float): The quantile step size.
    """
    def create_entry(
            problem_id: str,
            language: str,
            quintiles: Dict[str, str | float]
            ) -> Dict[str, str | float]:
        """
        Creates an Ordered Dictionary for the problem ID, langauge ID and
        quintiles (5%:95% in steps of 5%)

        Args:
            problem_id (str): The directory name within the CodeNet database.
            language (str): The langauge used to implement the solution.
            quintiles (Dict[str, str  |  float]): 5% - 95% (5% steps).

        Returns:
            _type_: _description_
        """
        return OrderedDict({"p_ID": problem_id, "lang": language, **quintiles})

    def process_file(
            file: str,
            ) -> None:
        """
        Processes files and computes the CPU performance quantiles.

        Args:
            file (str): The file to process.
        """
        metadata_df = pd.read_csv(os.path.join(folder_path, file))
        for language_ext in language_exts:
            quintiles = {
                str(q)[:4]: 
                round(
                    metadata_df[
                        (metadata_df["filename_ext"] == language_ext)
                        & (metadata_df["status"].str.strip() == "Accepted")
                    ]["cpu_time"].quantile(q), 5)
                for q in np.arange(
                    quantile_lower,
                    quantile_upper,
                    quantile_step
                )
            }
            entry = create_entry(file[:-4], language_ext, quintiles)
            entries.append(entry)
            print(entry)

    entries = []
    for file in os.listdir(folder_path):
        process_file(file)
    return entries

    # https://www.geeksforgeeks.org/python-loop-through-folders-and-files-in-directory/


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes the rows with the missing or duplicate data for the quantiles.

    Args:
        dataframe (pd.DataFrame): The dataframe to clean.

    Returns:
        pd.DataFrame: The cleaned dataframe with rows removed.
    """
    cleaned_df = df.dropna()
    return cleaned_df[cleaned_df['0.05'] != cleaned_df['0.95']]


if __name__ == '__main__':
    """
    Main entry point of the script.
    Orchestrates the methods to extract, process and clean the metadata.
    """
    FOLDER_PATH = "/Users/lavish/Downloads/Project_CodeNet/metadata"
    DATA_PATH = "perf_quintiles_by_lang.csv"
    language_exts = ["java", "js", "py"]
    quantile_params = [0.05, 1, 0.05]
    try:
        entries = process_files(FOLDER_PATH, language_exts, *quantile_params)
        processed_df = pd.DataFrame(entries)
        cleaned_df = clean_data(processed_df)
        cleaned_df.to_csv(DATA_PATH)
    except FileNotFoundError as e:
        print(f"{e}: Error locating the files in {FOLDER_PATH}")
    except Exception as e:
        print(f"{e}: Error while processing the files in {FOLDER_PATH}")
