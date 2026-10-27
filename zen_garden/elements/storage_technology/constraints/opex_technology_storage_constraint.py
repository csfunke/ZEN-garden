from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class OpexTechnologyStorageConstraint(GenericConstraint):
    """Calculate variable OPEX from storage throughput."""

    name = "constraint_opex_technology_storage"
    indices = (
        "set_technologies",
        "set_location",
        "set_years",
        "set_representative_hours",
    )
    masks = (PowerOperationMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        technologies = model.sets["set_storage_technologies"]
        nodes = model.sets["set_nodes"]
        cost = model.variables["cost_opex_variable"].sel(
            set_technologies=technologies, set_location=nodes
        )
        return (
            cost
            == model.parameters.opex_specific_variable
            * model.expressions["storage_throughput"]
        )
