import numpy as np

from zen_garden.elements.storage_technology.masks.energy_capacity_available_mask import (  # noqa: E501
    EnergyCapacityAvailableMask,
)
from zen_garden.model.component_types.variable import GenericVariable


class CapacityEnergy(GenericVariable):
    """Installed energy capacity of a storage technology."""

    name = "capacity_energy"
    symbol = r"E_{h,n,y}"
    indices = ("set_storage_technologies", "set_nodes", "set_years")
    doc = "Installed energy capacity of storage technology h at node n in year y."
    unit_category = {"energy_quantity": 1}
    masks = (EnergyCapacityAvailableMask,)

    @classmethod
    def get_bounds(cls, model_constructor, index_sets):
        """Return bounds that keep on/off storage formulations finite."""

        technologies_on_off = model_constructor.create_custom_set(
            ["set_storage_technologies", "set_on_off"]
        )[0]

        def capacity_bounds(technology, node, year):
            if technology not in technologies_on_off:
                return 0, np.inf

            model = model_constructor.optimization_model
            parameters = model.parameters.dict_parameters
            existing_capacity = 0
            for existing_id in model.sets["set_technologies_existing"][technology]:
                existing_lifetime = parameters.lifetime_existing[
                    technology, node, existing_id
                ]
                if existing_lifetime > parameters.lifetime[technology]:
                    is_available = year > (
                        existing_lifetime - parameters.lifetime[technology]
                    )
                else:
                    is_available = year <= existing_lifetime + 1
                if is_available:
                    existing_capacity += parameters.capacity_existing_energy[
                        technology, node, existing_id
                    ]

            maximum_addition = (
                len(model.sets["set_years"])
                * parameters.capacity_addition_max_energy[technology]
            )
            capacity_limit = parameters.capacity_limit_energy[technology, node, year]
            return 0, min(
                maximum_addition + existing_capacity,
                capacity_limit + existing_capacity,
            )

        return capacity_bounds
