"""Overnight CAPEX of storage-capacity additions."""

from zen_garden.model.component_types.expression import GenericExpression


class StorageOvernightCapex(GenericExpression):
    """Multiply storage power and energy additions by their specific CAPEX."""

    name = "storage_overnight_capex"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        model = model_constructor.optimization_model
        technologies = model.sets["set_storage_technologies"]
        nodes = model.sets["set_nodes"]
        addition = model.variables["capacity_addition"].sel(
            set_technologies=technologies, set_location=nodes
        )
        specific = model.parameters.capex_specific_storage.rename(
            set_storage_technologies="set_technologies", set_nodes="set_location"
        )
        return specific * addition
