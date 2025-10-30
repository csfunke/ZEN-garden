from zen_garden.__main__ import run_module
from zen_garden.postprocess.results.results import Results
from pathlib import Path
import shutil
import os

os.chdir(".\\data")
dataset = ".\\test_1j"
config = ".\\config.json"



# extract file path and name of the dataset
[dataset_path, dataset_name] = os.path.split(Path(dataset))
dataset_path = Path(dataset_path)
dataset_name = Path(dataset_name)

#create a copy of the original dataset the operation only model
dataset_op = dataset + "_operation"
if os.path.exists(dataset_op):
    shutil.rmtree(dataset_op)
shutil.copytree(dataset, dataset_op)

# run ZEN-garden on the original dataset
run_module(dataset = dataset, config = config)

# extract results on added capacity and investment
out_dir = dataset_path / "outputs" / dataset_name
r = Results(path=out_dir)

assert 'capacity_addition' in r.get_component_names('variable'), "Results have no variable named capacity addition"

capacity_addition = r.get_total('capacity_addition')
system = r.get_system()
capacity_addition = r.get_total('capacity_addition')

scenario_name = next(iter(r.solution_loader.scenarios.keys()))
r.solution_loader.scenarios[scenario_name]
r.get_system()
# delete created directory
shutil.rmtree(dataset_op)
