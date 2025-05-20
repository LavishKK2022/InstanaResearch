"""
Filters out code blocks that execute quickly,
based on a trained deep learning model.

This leaves a set of 'slow' code blocks,
that should be regenerated in the next step.
"""

from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification
)
from enum import Enum


class Classifier:
    """
    Performs binary classification on a list of code blocks.
    """
    TOKEN_MAX = 450     # Reduces Token Limit as described in dissertation.
    MODEL_NAME = "LavishKK/graphcodebert-slowcode-detector"
    # Hugging Face Hub repository

    class Label(Enum):
        """
        Classifier 'Fast', 'Slow' and 'Err' labels
        """
        SLOW = 1
        FAST = 0
        ERR = -1

        @staticmethod
        def pred_to_label(prediction):
            """
            Returns the Label associated with the Transformer prediction.

            Args:
                prediction: Prediction made by Binary classifier

            Returns:
                Associated label
            """
            match prediction:
                case 'LABEL_0':
                    return Classifier.Label.FAST
                case 'LABEL_1':
                    return Classifier.Label.SLOW
                case _:
                    return Classifier.Label.ERR

    def __init__(self):
        """
        Initialises the model, tokeniser and pipeline.
        """
        self.model = AutoModelForSequenceClassification.from_pretrained(
            Classifier.MODEL_NAME
        )
        self.tokenizer = AutoTokenizer.from_pretrained(Classifier.MODEL_NAME)
        self.pipeline = pipeline(
            task="text-classification",
            model=self.model,
            tokenizer=self.tokenizer
        )

    def __call__(self, *args, **kwargs):
        """
        Performs inference on the code inputs using the
        trained deep learning classifier.

        Returns:
            List of code blocks classified as 'Slow' code
        """
        slow_nodes = []
        for code_node in args:
            encoded = self.tokenizer.encode(
                code_node.method, max_length=5000, truncation=False)
            code_chunks = [
                self.tokenizer.decode(encoded[i:i+Classifier.TOKEN_MAX])
                for i in range(0, len(encoded), Classifier.TOKEN_MAX)
            ]
            chunks = list(map(lambda chunk: self.pipeline(
                chunk)[0]['label'], code_chunks))
            # Chunks input that exceeds the max token length
            classification = Classifier.Label.pred_to_label(
                max(['LABEL_1', 'LABEL_0'], key=chunks.count)
            )
            if classification == Classifier.Label.SLOW:
                slow_nodes.append(code_node)
        return slow_nodes
