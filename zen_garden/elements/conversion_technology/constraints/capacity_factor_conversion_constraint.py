from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class CapacityFactorConversionConstraint(GenericConstraint):
    """Capacity Factor Conversion."""

    name = "constraint_capacity_factor_conversion"
    indices = (
        "set_conversion_technologies",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )
    masks = (PowerOperationMask,)

    @classmethod
    def should_construct(cls, model_constructor):
        return bool(
            model_constructor.optimization_model.sets["set_conversion_technologies"]
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Load is limited by the installed capacity and the maximum load factor.

        Formulation:

        .. math::
            F^{\\mathrm{ref}}_{h,n,t} \\leq
            \\ell^{\\mathrm{max}}_{h,n,t}K_{h,n,y}

        Notation:

        :math:`m_{h,n,t}^{\\mathrm{max}}`: maximum load factor of the
        technology :math:`h` at node :math:`n` in time step :math:`t` of year
        :math:`y`
        :math:`K_{h,n,y}`: installed capacity of the technology :math:`h` at
        node :math:`n` in year :math:`y`
        :math:`F^{\\mathrm{ref}}_{h,n,t}`: reference carrier flow of the
        technology :math:`h` at node :math:`n` in time step :math:`t` of year
        :math:`y`

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        techs = model_constructor.optimization_model.sets["set_conversion_technologies"]
        nodes = model_constructor.optimization_model.sets["set_nodes"]
        term_capacity = (
            model_constructor.optimization_model.parameters.max_load.loc[
                techs, nodes, :, :
            ]
            * model_constructor.optimization_model.variables["capacity"].loc[
                techs, nodes, :
            ]
        ).rename(
            {
                "set_technologies": "set_conversion_technologies",
                "set_location": "set_nodes",
            }
        )
        term_reference_flow = model_constructor.optimization_model.expressions[
            "conversion_reference_flow"
        ]
        lhs = term_capacity - term_reference_flow
        rhs = 0
        constraints = lhs >= rhs

        return constraints
