from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class CapacityFactorStorageConstraint(GenericConstraint):
    """Capacity Factor Storage."""

    name = "constraint_capacity_factor_storage"
    indices = (
        "set_storage_technologies",
        "set_nodes",
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
        """Summary:
        Limits load of storage technologies by capacity and maximum load factor.

        Formulation:

        .. math::
            F^{\\mathrm{ch}}_{h,n,t}+F^{\\mathrm{dis}}_{h,n,t}\\leq
            \\ell^{\\mathrm{max}}_{h,n,t}K_{h,n,y}

        Notation:

        :math:`F^{\\mathrm{ch}}_{h,n,t}`: carrier flow into storage technology :math:`h`
        on node :math:`n` and time :math:`t` in year :math:`y`
        :math:`F^{\\mathrm{dis}}_{h,n,t}`: carrier flow out of storage
        technology :math:`h`on node :math:`n` and time :math:`t` in year :math:`y`
        :math:`\\ell^{\\mathrm{max}}_{h,n,t}`: maximum load factor for storage
        technology :math:`h` on node :math:`n` and time :math:`t` in year :math:`y`
        :math:`K_{h,n,y}`: storage capacity of storage technology :math:`h` on
        node :math:`n` in year :math:`y`

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        techs = model_constructor.optimization_model.sets["set_storage_technologies"]
        nodes = model_constructor.optimization_model.sets["set_nodes"]
        term_capacity = (
            model_constructor.optimization_model.parameters.max_load.loc[
                techs, nodes, :, :
            ]
            * model_constructor.optimization_model.variables["capacity"].loc[
                techs, "power", nodes, :
            ]
        ).rename(
            {
                "set_technologies": "set_storage_technologies",
                "set_location": "set_nodes",
            }
        )

        throughput = model_constructor.optimization_model.expressions[
            "storage_throughput"
        ].rename(
            set_technologies="set_storage_technologies",
            set_location="set_nodes",
        )
        lhs = term_capacity - throughput
        rhs = 0
        constraints = lhs >= rhs
        ### return
        return constraints
