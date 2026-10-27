from zen_garden.elements.technology.masks import CapacityAdditionEligibleMask
from zen_garden.model.component_types.constraint import GenericConstraint


class StorageTechnologyCapexConstraint(GenericConstraint):
    """Set storage overnight CAPEX from power- and energy-capacity additions."""

    name = "constraint_storage_technology_capex"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )
    masks = (CapacityAdditionEligibleMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        cost = model.variables["cost_capex_overnight"].sel(
            set_technologies=model.sets["set_storage_technologies"],
            set_location=model.sets["set_nodes"],
        )
        return cost == model.expressions["storage_overnight_capex"]
