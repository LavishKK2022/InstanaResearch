"""
Generative AI module, built on top of Ollama middleware.

This is used to send prompts, populated with data,
such as source code, programming language type or
method signature.
"""
from aioptim.utils.request import Conn
from dataclasses import dataclass
from aioptim.utils.config import Prompt


@dataclass
class Generator(Conn):
    """
    Built on top of the Conn(ection) class,
    this module uses generative AI to optimise slow code.
    """

    model: str
    url: str
    max_runs: int

    def __post_init__(self):
        """
        Ensure the prompts are included in the repository file
        """
        Prompt.validate()
        self.prompts = Prompt.get_contents()

    @staticmethod
    def _replace(prompt, replace_keywords):
        """
        Core function for the templating engine.
        Replaces keywords in prompts with dynamic context data.

        Args:
            prompt: The base prompt to augment
            replace_keywords: Dictionary consisting of keywords
                              and the data they represent

        Returns:
            Populated/complete prompt
        """
        for key, value in replace_keywords.items():
            prompt = prompt.replace(key, value)
        return prompt

    def generate(self, code, signature, language):
        """
        Generate source code from a slow code block

        Args:
            code: The referenced slow code
            signature: The signature of the method
            language: The language implementation of the code, e.g. Java

        Returns:
            The optimised code
        """
        return self._send(
            Generator._replace(
                self.prompts[Prompt.PromptKeys.CODE_GEN.value],
                {
                    "$CODE$": code,
                    "$LANGUAGE$": language,
                    "$SIGNATURE$": signature
                }
            )
        )

    def describe(self, code, language):
        """
        Describes source code for the later verification stages

        Args:
            code: The source code to evaluate
            language: The language implementation of the code, e.g. Java

        Returns:
           The description of the source code
        """
        return self._send(
            self._replace(
                self.prompts[Prompt.PromptKeys.DES_GEN.value],
                {
                    "$LANGUAGE$": language,
                    "$CODE$": code
                }
            )
        )

    def validate(self, description, generated_code, language):
        """
        Performs validation on the generated code

        Args:
            description: The description of the original code problem
            generated_code: The generated code
            language: The language implementation of the code, e.g. Java

        Returns:
            True if code is generated code is valid, False otherwise
        """
        codejudge_analysis = self._send(
            self._replace(
                self.prompts[Prompt.PromptKeys.CJ_ANALYSER.value],
                {
                    "$LANGUAGE$": language,
                    "$PROBLEM$": description,
                    "$CODE$": generated_code
                }
            )
        )
        codejudge_summarise = self._send(
            Generator._replace(
                self.prompts[Prompt.PromptKeys.CJ_SUMMARISE.value],
                {
                    "$ANALYSIS$": codejudge_analysis
                }
            )
        )

        return True if "yes" in codejudge_summarise.lower() else False

    def __bool__(self):
        """
        Checks if the models are available in the Ollama server host

        Returns:
            True if the model can be found in the host machine, False otherwise
        """
        models = super().get_req(
            endpoint="/api/tags",
            headers={},
            params={}
        )["models"]

        return self.model in map(lambda model: model["name"], models)

    def _send(self, prompt):
        """
        Sends the prompt to the Ollama host.
        This is conducted via the Ollama '/api/generate' endpoint.

        Args:
            prompt: The complete/populated prompt.

        Raises:
            ValueError: If the Ollama host does not generate a valid response

        Returns:
            The response of the request 
        """
        try:
            return super().post_req(
                endpoint="/api/generate",
                data={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                params={},
                headers={"Content-Type": "application/json"}
            )["response"]
        except Exception:
            raise ValueError("Invalid Response from Ollama API")
