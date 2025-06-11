from aioptim.services.generator import Generator
from aioptim.utils.config import Prompt
from dataclasses import dataclass


@dataclass
class AIClassifier(Generator):
    """
    Performs binary classification on a list of code blocks.
    """

    def __call__(self, *args, **kwds):
        """
        Performs inference on the code inputs using a generative AI model.

        Returns:
            List of code blocks classified as 'slow' code
        """
        slow_nodes = []
        for code_node in args:
            response = self._send(
                Generator._replace(
                    self.prompts[Prompt.PromptKeys.CODE_CLASSIFY.value],
                    {
                        "$CODE$": code_node
                    }
                )
            )
            if 'slow' in response.lower():
                slow_nodes.append(code_node)
        return slow_nodes
