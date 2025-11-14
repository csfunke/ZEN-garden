from zen_garden.__main__ import run_module
from zen_garden.wrapper import utils
from pathlib import Path
import shutil
import os
import argparse
import sys


def operation_scenarios(args=None,
                        config="./config.py",
                        dataset=None,
                        folder_output=None,
                        config_op=None,
                        dataset_op=None,
                        scenarios_op=None,
                        system_op=None,
                        job_index=None,
                        job_index_var="SLURM_ARRAY_TASK_ID",
                        delete_data='True'):
    """
    Currently only works if the original problem only has one scenario.

    """

    # read and parse ZEN-garden input arguments
    if args is None:
        args = sys.argv[1:]

    # parse the args
    description = "Run ZEN garden with a given config file. Per default, the" \
                  "config file will be read out from the current working " \
                  "directory. You can specify a config file with the --config "\
                  "argument. However, note that the output directory will " \
                  "always be the current working directory, independent of " \
                  "the dataset specified in the config file."
    parser = argparse.ArgumentParser(
        description=description,
        add_help=True,
        usage=
        "usage: python -m zen_garden.wrapper.operational_scenarios [-h] " \
        "[--config CONFIG] [--dataset DATASET] [--folder_output FOLDER_OUTPUT] "\
        "[--config_op CONFIG_OP] [--dataset_op DATASET_OP], " \
        "[--system_op SYSTEM_OP] [--scenarios_op SCENARIOS_OP] " \
        "[--job_index JOB_INDEX] [--job_index_var JOB_INDEX_VAR] "\
        "[--delete_data TRUE]"
    )
    # TODO make json config default
    parser.add_argument(
        "--config",
        required=False,
        type=str,
        default=config,
        help=
        "The config file used to run the capacity expansion model, defaults " \
        "to config.py in the current directory."
    )
    parser.add_argument(
        "--dataset",
        required=False,
        type=str,
        default=dataset,
        help=
        "Path to the dataset used for the run. IMPORTANT: This will overwrite "\
        " the config.analysis.folder_output attribute and the " \
        "config.solver.solver_dir attribute of the --config file!"
    )
    parser.add_argument(
        "--folder_output",
        required=False,
        type=str,
        default=folder_output,
        help=
        "Path to the folder where results of the capacity-expansion runs " \
        "are stored. IMPORTANT: This will overwrite the " \
        "config.analysis.folder_output attribute of the --config file! ."
    )
    parser.add_argument(
        "--config_op",
        required=False,
        type=str,
        default=config_op,
        help=
        "The config file used to run the operation-only model, defaults to " \
        " --config."
    )
    parser.add_argument(
        "--dataset_op",
        required=False,
        type=str,
        default=dataset_op,
        help=
        "Name of the dataset used for the operation-only runs. The outputs " \
        "will be saved under this dataset name"
    )
    parser.add_argument(
        "--scenarios_op",
        required=False,
        type=str,
        default=scenarios_op,
        help=
        "Path to the scenarios.json file used in the operation-only runs. " \
        "Defaults to the scenarios.json file from --dataset"
    )
    parser.add_argument(
        "--system_op",
        required=False,
        type=str,
        default=system_op,
        help=
        "Path to the systems.json file used in the operation-only runs. " \
        "Defaults to the system.json file from --dataset"
    )
    parser.add_argument(
        "--job_index",
        required=False,
        type=str,
        default=job_index,
        help=
        "A comma separated list (no spaces) of indices of the scenarios to " \
        "run, if None, all scenarios are run in sequence"
    )
    parser.add_argument(
        "--job_index_var",
        required=False,
        type=str,
        default=job_index_var,
        help=
        "Try to read out the job index from the environment variable " \
        "specified here. If both --job_index and " \
        "--job_index_var are specified, --job_index will be used."
    )
    parser.add_argument(
        "--delete_data",
        required=False,
        type=str,
        default=delete_data,
        help=
        "String ('True' or 'False') that specifies whether to delete the " \
        "operational dataset at the end of the process. Defaults to 'T'"
    )
    args = parser.parse_args(args)

    # clean inputs and set proper default values
    [dataset_path, dataset_name] = os.path.split(Path(args.dataset))
    if config_op is None:
        config_op = args.config
    if dataset_op is None:
        dataset_op = Path(dataset_path) / (dataset_name + "__operation")
    if system_op is None:
        system_op = Path(dataset_path) / dataset_name / "system.json"

    # run ZEN-garden on the original dataset
    run_module(dataset=dataset,
               config=config,
               folder_output=folder_output,
               job_index=job_index,
               job_index_var=job_index_var)

    #create new dataset for operational scenarios
    utils.copy_dataset(dataset,
                       dataset_op,
                       system=system_op,
                       scenarios=scenarios_op)

    # extract results on added capacity
    utils.capacity_addition_2_existing_capacity(
        Path(folder_output) / dataset_name, dataset_op)

    # turn off capacity_investment
    utils.modify_json(
        Path(dataset_op) / "system.json", {"allow_investment": False})

    # run operations only simulations
    print("Running Operational Scenarios -----------------------------")
    run_module(dataset=dataset_op,
               config=config_op,
               folder_output=folder_output)

    # delete created directory
    if args.delete_data.lower() == 'true':
        shutil.rmtree(dataset_op)


if __name__ == "__main__":
    # operation_scenarios(dataset = "./data/test_1j",
    #                       config="./data/config.json",
    #                       folder_output="./data/outputs")
    operation_scenarios()
