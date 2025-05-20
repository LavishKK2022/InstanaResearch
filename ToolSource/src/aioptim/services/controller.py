"""
Controller class to orchestrate the other modules.

This performs the end-to-end code retrival, extraction,
classification, regeneration and pushing the optimised code
back into the repository.
"""

import schedule
import time
import logging
from prefect import flow, task
from aioptim.utils.config import Config
from aioptim.services.classifier import Classifier
from aioptim.services.generator import Generator
from aioptim.services.processor import GithubProcessor
from aioptim.utils.state import State
from aioptim.services.instana import IBM
from aioptim.utils.info import details, get_col
from prefect.cache_policies import NO_CACHE

@task(name="push-code", log_prints=True, cache_policy=NO_CACHE)
def push_code(state):
    """
    If valid changes have been made. this method pushes
    these changes onto the repository,

    Args:
        state: The mutable state object
    """
    if state and hasattr(state, "slow_code_blocks") and state.slow_code_blocks:
        for slow_method in state.slow_code_blocks:
            if (
                hasattr(slow_method, "generated_code")
                    and slow_method.generated_code):
                state.processor.update_file(
                    slow_method, slow_method.generated_code)

@task(name="generate-code", log_prints=True)
def generate_code(state):
    """
    Underpins the code generation process.

    Calls the code generation module, ensuring the optimised
    code still behaves the same as the slow code.

    Args:
        state: The mutable state object

    Raises:
        LookupError: if the Ollama model does not exist
    """
    if state and hasattr(state, "slow_code_blocks") and state.slow_code_blocks:
        if state.generator:
            for slow_method in state.slow_code_blocks:
                current_runs = 0
                is_generated = False
                generated_code = ""
                while current_runs < state.generator.max_runs and not is_generated:
                    current_runs += 1
                    description = state.generator.describe(
                        slow_method.method,
                        slow_method.parent.language
                    )
                    generated_code = state.generator.generate(
                        slow_method.method,
                        slow_method.id,
                        slow_method.parent.language
                    )
                    is_generated = state.generator.validate(
                        description,
                        generated_code,
                        slow_method.parent.language
                    )
                slow_method.generated_code = generated_code
        else:
            raise LookupError(
                f"{state.generator.model} could not be found in Ollama")

@task(name="get-slow-code", log_prints=True, cache_policy=NO_CACHE)
def slow_code(state):
    """
    Calls the classifier to reduce the number of offending method blocks.
    The classifier filters out fast source of code.

    Args:
        state: The mutable state object
    """
    if state and hasattr(state, "fault_line") and state.fault_line:
        if len(state.fault_line) == 1:
            state.slow_code_blocks = list(state.fault_line)
        elif len(state.fault_line) > 1:
            state.slow_code_blocks = state.classifier(*state.fault_line)

@task(name="get-fault-line", log_prints=True)
def fault_line(state):
    """
    This creates numerous method traces for each
    instance of possibly slow code.

    Args:
        state: The mutable state object
    """
    state.fault_line = set()
    if state and hasattr(state, "endpoints") and state.endpoints:
        for endpoint in state.endpoints:
            extension = details(endpoint.technology, "extension")
            parser = details(endpoint.technology, "parser")
            files = state.processor[extension]
            for file in files:
                parser.parse_file_methods(file)
            parser.extend_file_methods(files)
            endpoint_method = parser.endpoint(files, endpoint.label)
            state.fault_line.update(parser.parse_method_calls(endpoint_method))

@task(name="get-slow-endpoints", log_prints=True)
def endpoints(state):
    """
    This calls the endpoints metrics and gets a 
    filtered list of endpoints.

    Args:
        state: The mutable state object
    """
    state.endpoints = state.ibm.filter_endpoints(
        state.ibm.get_endpoints(),
        state.threshold,
        get_col("technology")
    )

@flow(name="entry-point", log_prints=True)
def service(state):
    """
    Entry point of the service.
    Registers all the possible methods to execute.
    Resets the state on every full iteration.

    Args:
        state: The mutable state object
    """
    try:
        filters = [endpoints, fault_line, slow_code, generate_code, push_code]
        for process_filter in filters:
            process_filter(state)
        state.reset()
    except Exception as e:
        print(f"Error while running the service {e}...")
        exit(1)

def schedule_service(
    delay,
    threshold,
    contents,
    test_mode=False,
    state=None
):
    """
    This method registers the scheduled service.

    Args:
        delay: How often the service shoud run in minutes
        threshold: The minimum threshold to consider an endpoint - millisecond
        contents: The contents of a configuration file
        test_mode: Whether the system is currently being tested.
        state: The state to test the system under
    """

    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)
    if not state:   # pragma: no cover
        config = Config.ConfigKeys
        try:
            state = State(
                ibm=IBM(
                    contents[config.IBM_TENANT.value],
                    contents[config.IBM_UNIT.value],
                    contents[config.IBM_KEY.value],
                    contents[config.IBM_LABEL.value],
                    delay
                ),
                generator=Generator(
                    contents[config.MODEL.value],
                    contents[config.MODEL_PATH.value],
                    max_runs=3
                ),
                processor=GithubProcessor(
                    contents[config.GITHUB.value],
                    contents[config.REPOSITORY.value],
                    contents[config.BRANCH.value]
                ),
                classifier=Classifier(),
                threshold=threshold,
                delay=delay
            )
        except Exception as e:
            print(f"Error with configuring the application {e}...")
            exit(1)

    service(state)

    if not test_mode:  # pragma: no cover
        schedule.every(delay).minutes.do(
            service,
            state
        )
        while True:
            schedule.run_pending()
            time.sleep(1)
