"""
State object passed through the filters in the process chain.

Holds the Instana IBM object, code generator, github processor
and deep learning code classifier.

[1] https://stackoverflow.com/a/42303681
    Stack Overflow: willeM_ Van Onsem
    "Pythonic way to delete variable from self if it exists in a list"
"""

from dataclasses import dataclass
from aioptim.services.instana import IBM
from aioptim.services.generator import Generator
from aioptim.services.processor import GithubProcessor
from aioptim.services.classifier import Classifier


@dataclass
class State:
    """
    Reusable state object passed through the filters.

    Fields are mutated between processes and reset after
    complete runs.
    """
    ibm: IBM
    generator: Generator
    processor: GithubProcessor
    classifier: Classifier
    delay: int
    threshold: int

    def reset(self):
        """
        Resets the fields of the State object.

        Added fields are removed, except the original attributes:
        IBM, Generator, Processor, Classifier, delay and threshold.
            [1]
        """
        attribs = filter(
            lambda attribute: attribute not in ["ibm",
                                                "generator",
                                                "processor",
                                                "classifier",
                                                "delay",
                                                "threshold"
                                                ],
            self.__dict__
        )
        for attrib in list(attribs):
            delattr(self, attrib)
