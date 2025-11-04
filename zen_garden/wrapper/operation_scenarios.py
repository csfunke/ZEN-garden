from zen_garden.__main__ import run_module
from zen_garden.postprocess.results.results import Results
from pathlib import Path
import pandas as pd
import shutil
import os
import argparse
import sys
import json



def operational_scenarios(args = None, config = "./config.py", dataset = None, 
               folder_output = None, job_index = None, job_index_var = "SLURM_ARRAY_TASK_ID"):
    
    
    # read and parse ZEN-garden input arguments
    if args is None:
        args = sys.argv[1:]

    # parse the args
    description = "Run ZEN garden with a given config file. Per default, the config file will be read out from the " \
                  "current working directory. You can specify a config file with the --config argument. However, " \
                  "note that the output directory will always be the current working directory, independent of the " \
                  "dataset specified in the config file."
    parser = argparse.ArgumentParser(description=description, add_help=True, usage="usage: python -m zen_garden [-h] [--config CONFIG] [--dataset DATASET] [--job_index JOB_INDEX] [--job_index_var JOB_INDEX_VAR] [-- download_example EXAMPLE_NAME]")
    # TODO make json config default
    parser.add_argument("--config", required=False, type=str, default=config, help="The config file used to run the pipeline, "
                                                                                        "defaults to config.py in the current directory.")
    parser.add_argument("--dataset", required=False, type=str, default=dataset, help="Path to the dataset used for the run. IMPORTANT: This will overwrite the "
                                                                                  "config.analysis.dataset attribute of the config file!")
    parser.add_argument("--folder_output", required=False, type=str, default=folder_output, help="Path to the folder where results of the run are stored. IMPORTANT: This will overwrite the "
                                                                                        "config.analysis.folder_output attribute of the config file!")
    parser.add_argument("--job_index", required=False, type=str, default=job_index, help="A comma separated list (no spaces) of indices of the scenarios to run, if None, all scenarios are run in sequence")
    parser.add_argument("--job_index_var", required=False, type=str, default=job_index_var, help="Try to read out the job index from the environment variable specified here. "
                                                                                                         "If both --job_index and --job_index_var are specified, --job_index will be used.")
    args = parser.parse_args(args)
    
    # extract file path and name of the dataset
    [dataset_path, dataset_name] = os.path.split(Path(dataset))
    dataset_path = Path(dataset_path)

    #create a copy of the original dataset the operation only model
    dataset_op = dataset_path / (dataset_name + "_operation")
    config_op = dataset_path / ("config_operation.json")
    if os.path.exists(dataset_op):
        shutil.rmtree(dataset_op)
    if os.path.exists(config_op):
        os.remove(config_op)
    shutil.copytree(dataset, dataset_op)
    shutil.copyfile(args.config, config_op)

    # run ZEN-garden on the original dataset
    run_module(dataset = dataset, config = config, 
               folder_output = folder_output, job_index = job_index, 
               job_index_var = job_index_var)

    # extract results on added capacity
    out_dir = dataset_path / "outputs" / dataset_name
    capacity_addition_2_existing_capacity(out_dir, dataset_op)
    modify_json(
        dataset_op / "system.json", 
        {"allow_investment": False}
    )

    # run operations only simulations
    print("Running Operational Scenarios")       
    run_module(dataset = dataset_op, config = config_op)

    # delete created directory
    shutil.rmtree(dataset_op)
    os.remove(config_op)


def capacity_addition_2_existing_capacity(out_dir, dataset_op):
    """
    out_dir ... directory of simulation_ouputs
    dataset_op ... new model dataset to which to add capacity additions as 
    existing capacities.
    """
    r = Results(path=out_dir)
    assert 'capacity_addition' in r.get_component_names('variable'), "Results have no variable named capacity addition"
    capacity_addition = r.get_total('capacity_addition')
    system = r.get_system()
    capacity_addition = r.get_total('capacity_addition')

    # reindex capacity addition so that it contains values for all combinations
    # of technologies and nodes
    system = r.get_system()
    index_full = pd.MultiIndex.from_product(
        [system.set_technologies, ["power", "energy"], system.set_nodes],
        names = capacity_addition.index.names
    )
    capacity_addition = capacity_addition.reindex(index_full)

    # add as capacities to input files of operations simulation

    #  Iterate over technology types: conversion, transport, storage
    technologies = {
        "set_conversion_technologies": system.set_conversion_technologies,
        "set_transport_technologies": system.set_transport_technologies,
        "set_storage_technologies": system.set_storage_technologies
    }
    for element_name, elements in technologies.items():
        print(element_name)
        # Iterate over each technology in that type
        for tech in elements:
            print(tech)
            tech_folder_op = (
                dataset_op / 
                "set_technologies" / 
                element_name /
                tech
            )
            # Repeat for power capacity and energy capacity separately
            for (type, suffix) in [("power",""), ("energy", "_energy")]:
                capacity_addition_tech = capacity_addition.loc[(tech, type)]
                capacity_addition_tech = (
                    capacity_addition_tech.stack().dropna().reset_index()
                )
                if capacity_addition_tech.shape[0] != 0:
                    # rename columns
                    capacity_addition_tech = (
                        capacity_addition_tech.rename(
                            columns = {
                                'location': 'node',
                                'level_1': 'year_construction',
                                0: 'capacity_existing' + suffix
                            }
                        )
                    )
                    # load existing file
                    capacity_existing = pd.read_csv(
                        tech_folder_op / ("capacity_existing" + suffix + ".csv"),
                    )
                    # merge
                    capacity_existing = pd.concat(
                        [capacity_existing, capacity_addition_tech]
                    ).reset_index(drop = True)

                    # sum capacities
                    capacity_existing = capacity_existing.groupby(
                        by = ["node", "year_construction"]
                    ).sum()

                    # save
                    capacity_addition_tech.to_csv(
                        tech_folder_op / ("capacity_existing" + suffix + ".csv"),
                        mode = 'w',
                        header = True,
                        index = False
                    )

def modify_json(file_path, change_dict):
    
    """
    Modify a json file according to a change dictionary
    """
    with open(file_path, 'r+') as f:
        data = json.load(f)
        data['id'] = 134 # <--- add `id` value.
        f.seek(0)        # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()     # remove remaining part

if __name__ == "__main__":
    operational_scenarios(dataset = "./data/test_1j", config="./data/config.json")
