from zen_garden.postprocess.results.results import Results
from pathlib import Path
import pandas as pd
import shutil
import os
import json


def capacity_addition_2_existing_capacity(out_dir, dataset_op):
    """
    out_dir ... directory of simulation_ouputs
    dataset_op ... new model dataset to which to add capacity additions as 
    existing capacities.
    """
    out_dir = Path(out_dir)
    dataset_op = Path(dataset_op)

    # load results
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
                    ).sum().reset_index()
                    
                    # save
                    capacity_existing.to_csv(
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
        
        # write new attribute
        for attr, value in change_dict.items():
            data[attr] = value # <--- set attribute value
        
        # write file
        f.seek(0)        # move cursor to beginning of file
        json.dump(data, f, indent=4)
        f.truncate()     # remove leftover pieces if old file was longer


def copy_dataset(old_dataset, new_dataset, system, scenarios = None):

    #create new dataset for operational scenarios
    if os.path.exists(new_dataset):
        shutil.rmtree(new_dataset)
    os.makedirs(new_dataset)
    shutil.copytree(
        Path(old_dataset) / "energy_system", 
        Path(new_dataset) / "energy_system"
    )
    shutil.copytree(
        Path(old_dataset) / "set_carriers", 
        Path(new_dataset) / "set_carriers"
    )
    shutil.copytree(
        Path(old_dataset) / "set_technologies", 
        Path(new_dataset) / "set_technologies"
    )
    shutil.copyfile(system, Path(new_dataset) / "system.json")
    if scenarios is not None:
        shutil.copyfile(scenarios, Path(new_dataset) / "scenarios.json")