"""
AIOPTIM command line input entry point.
"""

import typer
from aioptim.utils.config import Config
from typing_extensions import Annotated
from aioptim.services.controller import schedule_service
from colorist import Color
app = typer.Typer(pretty_exceptions_enable=False)
Y = Color.YELLOW
O = Color.OFF
C = Color.CYAN
G = Color.GREEN


@app.command("setup")
def store_params(
    ibm_tenant: Annotated[
        str, typer.Option(
            "-tenant",
            help="IBM tenant from https://unit-tenant.instana.io",
            rich_help_panel="IBM Details",
            prompt=(
                f"{Y}Input{O} {C}IBM tenant{O} "
                f"from https://unit-{C}TENANT{O}.instana.io"
            )
        )
    ],
    ibm_unit: Annotated[
        str, typer.Option(
            "-unit",
            help="IBM unit from https://unit-tenant.instana.io",
            rich_help_panel="IBM Details",
            prompt=(
                f"{Y}Input{O} {C}IBM unit{O} "
                f"from https://{C}UNIT{O}-tenant.instana.io"
            )
        )
    ],
    ibm_apikey: Annotated[
        str, typer.Option(
            "-api",
            help="IBM user API Key",
            rich_help_panel="IBM Details",
            prompt=(f"{Y}Input{O} {C}IBM API{O} key")
        )
    ],
    ibm_label: Annotated[
        str, typer.Option(
            "-label",
            help="IBM label associated with applications perspective",
            rich_help_panel="IBM Details",
            prompt=(
                f"{Y}Input{O} the {C}label{O} "
                f"for the applications perspective"
            )
        )
    ],
    github_token: Annotated[
        str, typer.Option(
            "-pat",
            help="GitHub PAT with repository read/write permissions",
            rich_help_panel="GitHub Details",
            prompt=(
                f"{Y}Input{O} valid "
                f"{C}Github PAT{O} with read/write permissions"
            )
        )
    ],
    repository_name: Annotated[
        str, typer.Option(
            "-repo",
            help="The name of the repository with read/write permissions",
            rich_help_panel="GitHub Details",
            prompt=(
                f"{Y}Input{O} the {C}repository{O} with read/write permissions"
            )
        )
    ],
    repository_branch: Annotated[
        str, typer.Option(
            "-branch",
            help="The name of the deployment branch",
            rich_help_panel="GitHub Details",
            prompt=(
                f"{Y}Input{O} the name of "
                f"the {C}deployment branch{O}"
            )
        )
    ] = "main",
    model: Annotated[
        str, typer.Option(
            "-model",
            help="The Ollama model to use when generating code",
            rich_help_panel="Ollama Details",
            prompt=(
                f"{Y}Input{O} the {C}Ollama model{O} "
                f"to use to generate code"
            )
        )
    ] = "codellama",
    model_path: Annotated[
        str, typer.Option(
            "-ollama",
            help="The API path for the Ollama model [PATH]:[PORT]",
            rich_help_panel="Ollama Details",
            prompt=(
                f"{Y}Input{O} the URL "
                f"{C}path to the Ollama model [PATH]:[PORT]{O}"
            )
        )
    ] = "http://localhost:11434"
):
    """
    Sets the parameters for the AI Optimiser tool.

    NOTE: Ensure the GitHub PAT is associated with a single repository\n
    NOTE: Ensure the IBM API Key is prefixed with the 'apiToken'\n
    """
    Config.create_file()
    Config(
        tenant=ibm_tenant,
        unit=ibm_unit,
        api=ibm_apikey,
        label=ibm_label,
        github=github_token,
        repository_name=repository_name,
        repository_branch=repository_branch,
        model=model,
        model_path=model_path
    ).store_data()

    print(f"{G}Setup completed successfully{O}")


@app.command("start")
def start(
    threshold: Annotated[
        int, typer.Argument(
            help="The maximum endpoint threshold in millisecond",
            rich_help_panel="Running Parameters"
        ),
    ] = 500,
    delay: Annotated[
        int, typer.Argument(
            help="How often (minutes) to run the Instana service",
            rich_help_panel="Running Parameters"
        )
    ] = 10,
):
    """
    Checks the setup parameters and starts the service.
    """
    try:
        Config.validate()
        schedule_service(delay, threshold, Config.get_contents())
    except Exception as e:
        print(f"Error while running the application: {e}")
        exit(1)


if __name__ == "__main__":  # pragma: no cover
    app()
