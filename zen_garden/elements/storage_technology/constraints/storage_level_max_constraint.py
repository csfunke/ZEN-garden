from zen_garden.elements.storage_technology.masks import StorageStateMask
from zen_garden.model.component_types.constraint import GenericConstraint


class StorageLevelMaxConstraint(GenericConstraint):
    """Storage Level Max."""

    name = "constraint_storage_level_max"
    indices = (
        "set_storage_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours_storage",
    )
    masks = (StorageStateMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_storage_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Limit maximum storage level to capacity.

        Formulation:

        .. math::
            S^{\\mathrm{level}}_{h,n,\\tilde{t}} \\le K^{\\mathrm{energy}}_{h,n,y}

        Notation:

        :math:`S^{\\mathrm{level}}_{h,n,\\tilde{t}}`: storage level of storage
        technology :math:`h` at node :math:`n` in storage time step :math:`\\tilde{t}`
        of year :math:`y`
        :math:`K^{\\mathrm{energy}}_{h,n,y}`: energy capacity of storage technology
        :math:`h` on node :math:`n` in year :math:`y`

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        techs = model_constructor.optimization_model.sets["set_storage_technologies"]
        nodes = model_constructor.optimization_model.sets["set_nodes"]
        capacity = model_constructor.optimization_model.variables[
            "capacity_energy"
        ].sel(set_nodes=nodes, set_storage_technologies=techs)
        storage_level = model_constructor.optimization_model.variables["storage_level"]
        lhs = storage_level - capacity
        rhs = 0
        constraints = lhs <= rhs

        return constraints
