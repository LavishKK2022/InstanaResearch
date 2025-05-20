from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import Dataset
import pandas as pd
import numpy as np
import evaluate
import sklearn
import os

DATA_PATH = ""          # Input the path to the IBM CodeNet Dataset
META_DATASET_PATH = ""  # Input the path to the IBM CodeNet Metadata
MODEL_PATH = ""         # Where to store the trained model
TRAINING_LOG = ""       # Where to store the model checkpoints
LOGGING_DIR = ""        # Where to store the training logs
TRAIN_PARAM = 0.8
TEST_PARAM = 0.2
meta_df = pd.read_csv(META_DATASET_PATH)
PER_DEVICE_BATCH_SIZE = 64

model_name = "microsoft/graphcodebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

lang_to_ext = {"Java": "java", "Python": "py", "JavaScript": "js"}
combined_metrics = evaluate.combine(["accuracy", "f1", "precision", "recall"])

files_processed = 0


def dataset_gen():
    """
    Generates the dataset based on CodeNet annotated data.

    Yields:
        Code and associated annotation.
    """
    global files_processed
    for _, row in meta_df.iterrows():
        try:
            # Extract data from the CodeNet folder to feed into the model
            path = os.path.join(
                DATA_PATH,
                row["p_ID"],
                row["Lang"],
                f"{row['s_ID']}.{lang_to_ext[row['Lang']]}",
            )
            code = ""
            with open(path) as f:
                code = f.read()
            files_processed += 1
            yield {"code": code, "label": row["Label"]}
        except Exception as e:
            print(f"{e}: An error was caught during dataset generation")


def compute_metrics(eval_pred):
    """
    Generates the metrics for the F1 score, Precision,
    Recall and Accuracy.

    Args:
        eval_pred: logits, labels for the prediction.

    Returns:
        The computed metrics.
    """
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return combined_metrics.compute(predictions, labels)


def tokenize_function(row):
    """
    Convert the code to tokens.

    Args:
        row: code and label row

    Returns:
        Tokenised code
    """
    return tokenizer(row["code"], padding="max_length", truncation=True)


dataset = Dataset.from_generator(dataset_gen, keep_in_memory=True)
dataset = dataset.map(tokenize_function, batched=True, keep_in_memory=True)
dataset = dataset.train_test_split(
    test_size=TEST_PARAM, train_size=TRAIN_PARAM, shuffle=True, keep_in_memory=True
)

training_arguments = TrainingArguments(
    output_dir=TRAINING_LOG,
    logging_dir=LOGGING_DIR,
    logging_steps=500,
    logging_strategy="steps",
    eval_steps=1000,
    eval_strategy="steps",
    save_strategy="epoch",
    learning_rate=2e-5,
    num_train_epochs=3.0,
    per_device_eval_batch_size=PER_DEVICE_BATCH_SIZE,
    per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,
)

trainer = Trainer(
    model=model,
    args=training_arguments,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    compute_metrics=compute_metrics,
)

trainer.train()                                                 # Start training
trainer.save_model(MODEL_PATH)                                  # Save Model
evaluation_results = trainer.evaluate()                         # Evaluate the model
print(f"Evaluation Results: \n {evaluation_results}")
print(f"Files processed: {files_processed}/{len(meta_df)}")