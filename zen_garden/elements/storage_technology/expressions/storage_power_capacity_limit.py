"""Power-capacity limit for storage operation."""

from zen_garden.model.component_types.expression import GenericExpression


class StoragePowerCapacityLimit(GenericExpression):
    """Select and align storage power-capacity limits."""

    name = "storage_power_capacity_limit"
    indices = ("set_storage_technologies", "set_nodes", "set_years")

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct select and align storage power-capacity limits.

        Summary:
            Select and align storage power-capacity limits.

        Formulation:

        .. math::

            \\bar k_{h,power,n,y}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
        optimization_model = model_constructor.optimization_model
        return optimization_model.parameters.capacity_limit.rename(
            {
                "set_technologies": "set_storage_technologies",
                "set_location": "set_nodes",
            }
        ).sel(
            set_storage_technologies=optimization_model.sets[
                "set_storage_technologies"
            ],
            set_nodes=optimization_model.sets["set_nodes"],
            set_capacity_types="power",
        )
