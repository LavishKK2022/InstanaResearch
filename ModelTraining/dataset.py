"""
Annotates the code samples based on the execution time,
lower and upper quantiles.
"""

import pandas as pd
from enum import Enum
from typing import List, Dict
from collections import OrderedDict
import os


class Label(Enum):
    """
    Labels for the code.
    """
    SLOW = 1
    FAST = 0
    ERR = -1

    @staticmethod
    def classify(c_time: float, l_range: float, u_range: float):
        """
        Classifies CPU performance based on cpu time:
        c_time < l_range -> FAST
        c_time > u_range -> SLOW
        l_range <= c_time <= u_range -> ERR

        Args:
            c_time (float): The CPU run time used to classify the code.
            l_range (float): The lower quantile values.
            u_range (float): The upper quantile values.

        Returns:
            Label: Classifying the execution of code.
        """
        if c_time < l_range:
            return Label.FAST
        elif c_time > u_range:
            return Label.SLOW
        return Label.ERR


def state(problem_id: str, metadata_path: str, submission_ID: str) -> bool:
    """
    Checks if the submission has been accepted (as in dataset).
    This is because code classification will only be performed on code
    samples that have been accepted as working solutions.

    Args:
        problem_id (str): The problem identifier for the code solution.
        metadata_path (str): The path to the metadata file.
        submission_ID (str): The submission ID to check.

    Returns:
        bool: Whether the solution is accepted as working.
    """
    md = pd.read_csv(os.path.join(metadata_path, f"{problem_id}.csv"))
    return (
        md[
            md["submission_id"] == submission_ID
        ]["status"].str.lower() == "accepted"
    ).item()


def cpu_time(problem_id: str, metadata_path: str, submission_ID: str) -> float:
    """
    Retrieves the CPU performance time for the submission.

    Args:
        problem_id (str): The problem identifier for the code solution.
        metadata_path (str): The path to the metadata file.
        submission_ID (str): The submission ID to check.

    Returns:
        float: The CPU performance time for the submission.
    """
    md = pd.read_csv(os.path.join(metadata_path, f"{problem_id}.csv"))
    return (md[md["submission_id"] == submission_ID]["cpu_time"]).item()


def process(data_path: str,
            quantile_path: str,
            metadata_path: str,
            l_bound: str,
            u_bound: str
            ) -> List[Dict[str, str | int]]:
    """
    Processes the files to create a list of labelled submission data.
    Data for which the CPU performance time is below the lower bound quantile
    is marked as SLOW.
    Data for which the CPU performance time is above the upper bound quantile
    is marked as FAST.

    Args:
        data_path (str): The path to the data file.
        quantile_path (str): The path to the file describing the quantiles.
        metadata_path (str): The path to the metadata file.
        l_bound (str): The lower bound to classify as SLOW.
        u_bound (str): The upper bound to classify as FAST.

    Returns:
        List[Dict[str, str | int]]: Entries for the labelled submission data.
    """
    def create_entry(
                    problem_id: str,
                    language: str,
                    submission_id: str,
                    label: Label
                ) -> Dict[str, str | int]:
        """
        Creates an Ordered Dictionary for the problem ID, langauge,
        submission ID and labels.

        Args:
            problem_id (str): The problem identifier for the code solution.
            language (str): The programming laguage of the code solution.
            submission_id (str): The submission ID to check.
            label (Label): The label for the code solution.

        Returns:
            Dict[str, str | int]: An Ordered Dictionary containing the
            problem ID, language, submission ID and the respective labels.
        """
        return OrderedDict({
            "p_ID": problem_id,
            "Lang": language,
            "s_ID": submission_id,
            "Label": label.value,
        })

    def process_files(
            problem_id: str,
            language: str,
            l_bound_val: float,
            u_bound_val: float
            ) -> None:
        """
        Process the files, by filtering 'Accepted' submissions and extracting
        submissions where the CPU time lies under the lower bound or above
        the upper bound.
    
        This is to later aid with training by having preprocessed submissions.

        Args:
            problem_id (str): The problem identifier for the code solution.
            language (str): The programming language of the code solution.
            l_bound_val (float): The lower bound CPU time for the SLOW code.
            u_bound_val (float): The upper bound CPU time for the FAST code.
        """
        path = os.path.join(data_path, problem_id, language)
        for file in os.listdir(path):
            submission_ID = file[:10]
            is_accepted = state(problem_id, metadata_path, submission_ID)
            if is_accepted:
                c_time = cpu_time(problem_id, metadata_path, submission_ID)
                label = Label.classify(c_time, l_bound_val, u_bound_val)
                if label.value >= 0:
                    entries.append(
                        create_entry(
                            problem_id,
                            language,
                            submission_ID,
                            label
                        )
                    )

    entries = []
    lang_to_folder = {"java": "Java", "py": "Python", "js": "JavaScript"}
    quantiles_df = pd.read_csv(quantile_path)
    for _, row in quantiles_df.iterrows():
        process_files(
            row["p_ID"], 
            lang_to_folder[row["lang"]],
            row[l_bound],
            row[u_bound]
        )
    return entries


if __name__ == "__main__":
    """
    Main entry point of the script.
    Orchestrates the creation of labelled submission data.
    """
    PERF_QUANTILES_PATH = (
        "/Users/lavish/Desktop/Project/MetadataTool/data/perf_quintiles_by_lang.csv"
    )
    DATA_PATH = "/Users/lavish/Downloads/Project_CodeNet/data"
    METADATA_PATH = "/Users/lavish/Downloads/Project_CodeNet/metadata"
    SUBMISSION_PATH = "labelled_submissions.csv"
    bounds = ["0.25", "0.75"]

    try:
        entries = process(
            DATA_PATH,
            PERF_QUANTILES_PATH,
            METADATA_PATH,
            *bounds
        )
        processed_df = pd.DataFrame(entries)
        processed_df.to_csv(SUBMISSION_PATH)
    except FileNotFoundError as e:
        print(f"{e}: Error locating the files in {DATA_PATH}")
    except Exception as e:
        print(f"{e}: Error while processing the files in {DATA_PATH}")
