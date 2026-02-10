import argparse
import json
import os
from pathlib import Path

from zen_garden.cli.zen_garden_cli import build_parser
from zen_garden.wrapper.operation_scenarios import operation_scenarios


def build_parser_op() -> argparse.ArgumentParser:

    # load parser from zen-garden
    parser = build_parser()

    parser.add_argument(
        "--config_op",
        required=False,
        type=str,
        default=None,
        help="The config file used to run the operation-only model, defaults to "
        " --config.",
    )
    parser.add_argument(
        "--dataset_op",
        required=False,
        type=str,
        default=None,
        help="Name of the dataset used for the operation-only runs. The outputs "
        "will be saved under this dataset name",
    )
    parser.add_argument(
        "--scenarios_op",
        required=False,
        type=str,
        default=None,
        help="Path to the scenarios.json file used in the operation-only runs. "
        "Defaults to the scenarios.json file from --dataset",
    )
    parser.add_argument(
        "--job_index_op",
        type=str,
        required=False,
        default=None,
        help="Comma-separated list of scenario indices in the operational"
        "problem. If omitted, the environment variable specified by "
        "--job_index_var is used.",
    )
    parser.add_argument(
        "--delete_data",
        action="store_true",
        help="Deletes the created operation-only models upon termination to avoid "
        "cluttering the data directory",
    )

    # add parser description
    parser.description = (
        "Run ZEN garden with a given config file. Per default, the"
        "config file will be read out from the current working "
        "directory. You can specify a config file with the --config "
        "argument. However, note that the output directory will "
        "always be the current working directory, independent of "
        "the dataset specified in the config file."
    )

    parser.usage = (
        "usage: python -m zen_garden.wrapper.operational_scenarios [-h] "
        "[--config CONFIG] [--dataset DATASET] [--folder_output FOLDER_OUTPUT] "
        "[--job_index JOB_INDEX] [--job_index_var JOB_INDEX_VAR] "
        "[--scenarios_op SCENARIOS_OP] "
        "[--delete_data] [--use_existing]"
    )

    return parser


def parse_index(arg: str | None) -> list[int] | None:
    """Parse a comma-separated list of integer indices.

    This helper is used to parse CLI arguments that specify one or
    more job indices. If the argument is omitted or empty, ``None`` is returned.

    Args:
        arg (str | None): Comma-separated list of integers (e.g. "0,3,5"),
            or ``None``.

    Returns:
        list[int] | None: A list of parsed integers if ``arg`` is provided,
        otherwise ``None``.
    """
    if not arg:
        return None
    return [int(i) for i in arg.split(",")]


def get_number_of_operational_scenarios(dataset: str, scenarios_op: str) -> int:
    """Return the number of operational scenarios defined in a scenarios file.

    The scenarios file is expected to be a JSON file located inside the dataset
    directory. One additional scenario is counted to account for the base
    (non-operational) scenario.

    Args:
        dataset (str): Path to the dataset directory.
        scenarios_op (str | None): Filename of the operational scenarios JSON
            file. If ``None``, defaults to ``"scenarios.json"``.

    Returns:
        int: Total number of operational scenarios, including the base scenario.

    Raises:
        FileNotFoundError: If the scenarios file does not exist.
        json.JSONDecodeError: If the scenarios file cannot be parsed as JSON.
    """
    if scenarios_op is None:
        scenarios_op = "scenarios.json"
    scenarios_op_fp = Path(dataset) / scenarios_op
    if not scenarios_op_fp.exists():
        raise FileNotFoundError(
            f"Operational scenarios file not found: {scenarios_op_fp}"
        )

    with open(scenarios_op_fp, "r") as f:
        data = json.load(f)

    return len(data) + 1  # plus one for base scenario


def resolve_job_index(
    args: argparse.Namespace,
) -> tuple[list[int] | None, list[int] | None]:
    """Resolve job indices from CLI arguments or a SLURM array environment.

    Job indices may be provided explicitly via CLI arguments. If neither
    ``args.job_index`` nor ``args.job_index_op`` is specified, this function
    falls back to deriving indices from the environment variable specified by
    ``args.job_index_var`` (e.g. ``SLURM_ARRAY_TASK_ID``).

    The environment-based index is mapped to a pair of indices corresponding to
    a Cartesian product of model runs and operational scenarios.

    Args:
        args: Parsed command-line arguments. Expected to provide the attributes
            ``job_index``, ``job_index_op``, ``job_index_var``, ``dataset``,
            and ``scenarios_op``.

    Returns:
        tuple[list[int] | None, list[int] | None]: A tuple
        ``(job_index, job_index_op)``. Each element is either a list containing
        a single index or ``None`` if no index could be resolved.
    """
    job_index = parse_index(args.job_index)
    job_index_op = parse_index(args.job_index_op)

    if job_index is None and job_index_op is None:
        env_value = os.environ.get(args.job_index_var)

        if env_value is not None:
            array_id = int(env_value)

            n_op = get_number_of_operational_scenarios(args.dataset, args.scenarios_op)

            job_index = [array_id // n_op]
            job_index_op = [array_id % n_op]

    return job_index, job_index_op


def create_zen_operation_cli() -> None:
    # create parser and parse command line argument
    parser = build_parser_op()
    args = parser.parse_args()

    # Make dataset a required argument
    if args.dataset is None:
        raise parser.error("Missing required argument --dataset.")

    job_index, job_index_op = resolve_job_index(args)

    # run operation scenarios
    operation_scenarios(
        config=args.config,
        dataset=args.dataset,
        folder_output=args.folder_output,
        job_index=job_index,
        job_index_op=job_index_op,
        scenarios_op=args.scenarios_op,
        delete_data=args.delete_data,
    )


if __name__ == "__main__":

    create_zen_operation_cli()
