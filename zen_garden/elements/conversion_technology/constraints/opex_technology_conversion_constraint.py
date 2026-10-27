from zen_garden.elements.technology.masks import PowerOperationMask
from zen_garden.model.component_types.constraint import GenericConstraint


class OpexTechnologyConversionConstraint(GenericConstraint):
    """Calculate variable OPEX from conversion reference flow."""

    name = "constraint_opex_technology_conversion"
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
        """Construct calculate variable opex from conversion reference flow.

        Summary:
            Calculate variable OPEX from conversion reference flow.

        Formulation:

        .. math::

            C^{opex,var}=k^{opex,var}F^{ref}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        model = model_constructor.optimization_model
        technologies = model.sets["set_conversion_technologies"]
        nodes = model.sets["set_nodes"]
        cost = (
            model.variables["cost_opex_variable"]
            .sel(set_technologies=technologies, set_location=nodes)
            .rename(
                set_technologies="set_conversion_technologies",
                set_location="set_nodes",
            )
        )
        factor = model.parameters.opex_specific_variable.rename(
            set_technologies="set_conversion_technologies",
            set_location="set_nodes",
        )
        return cost == factor * model.expressions["conversion_reference_flow"]
