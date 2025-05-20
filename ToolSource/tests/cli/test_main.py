from aioptim.cli.main import start, store_params
from unittest.mock import patch
from aioptim.utils.config import Config
from unittest.mock import MagicMock


def test_start():
    delay, threshold, config = 5, 500, MagicMock()
    id = 999
    config.id = id
    with patch("aioptim.cli.main.schedule_service") as mock_schedule:
        with patch.object(Config, "validate", return_value=None):
            with patch.object(Config, "get_contents", return_value=config):
                start(threshold, delay)
                assert mock_schedule.call_args[0][0] == delay
                assert mock_schedule.call_args[0][1] == threshold
                assert mock_schedule.call_args[0][2].id == id


def test_setup():
    param = {
        "tenant": "tenant",
        "unit": "ibm_unit",
        "api": "ibm_apikey",
        "label": "ibm_label",
        "github": "github_token",
        "repository_name": "repository_name",
        "repository_branch": "repository_branch",
        "model": "model",
        "model_path": "model_path"
    }

    with patch.object(Config, "create_file", return_value=None) as mock_create:
        with patch.object(Config, "store_data") as mock_store:
            store_params(
                param["tenant"],
                param["unit"],
                param["api"],
                param["label"],
                param["github"],
                param["repository_name"],
                param["repository_branch"],
                param["model"],
                param["model_path"]
            )
            mock_store.assert_called_once()
            mock_create.assert_called_once()
