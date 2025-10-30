from zen_garden.__main__ import run_module
from zen_garden.postprocess.results.results import Results
from pathlib import Path
import pandas as pd
import shutil
import os

os.chdir(".\\data")
dataset = ".\\test_1j"
config = ".\\config.json"



# extract file path and name of the dataset
[dataset_path, dataset_name] = os.path.split(Path(dataset))
dataset_path = Path(dataset_path)

#create a copy of the original dataset the operation only model
dataset_op = dataset_path / (dataset_name + "_operation")
if os.path.exists(dataset_op):
    shutil.rmtree(dataset_op)
shutil.copytree(dataset, dataset_op)

# run ZEN-garden on the original dataset
run_module(dataset = dataset, config = config)

# extract results on added capacity
out_dir = dataset_path / "outputs" / dataset_name
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

# run operations only simulations
print("Running Operational Scenarios")       
run_module(dataset = dataset_op, config = config)


# delete created directory
shutil.rmtree(dataset_op)
