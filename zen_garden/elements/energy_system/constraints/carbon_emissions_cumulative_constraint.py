import xarray as xr

from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsCumulativeConstraint(GenericConstraint):
    """Carbon Emissions Cumulative."""

    name = "constraint_carbon_emissions_cumulative"
    indices = ("set_years",)

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Cumulative carbon emissions over time.

        Formulation:

        .. math::
            \\text{First planning period } y = y_0, \\quad
            M_y^{\\mathrm{cum}} = m_0^{\\mathrm{cum}}+M_y
        .. math::
            \\text{Subsequent periods } y > y_0, \\quad M_y^{\\mathrm{cum}}
            = M_{y-1}^{\\mathrm{cum}} + (\\Delta y-1)M_{y-1}+M_y

        Notation:

        :math:`\\Delta y`: interval between planning periods
        :math:`M_y`: annual carbon emissions in year :math:`y`
        :math:`M_y^{\\mathrm{cum}}`: cumulative carbon emissions in year :math:`y`
        :math:`m_0^{\\mathrm{cum}}`: cumulative emissions before the modeled horizon

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        m = [
            True if year == model_constructor.model_schema.set_years[0] else False
            for year in model_constructor.model_schema.set_years
        ]

        lhs = model_constructor.optimization_model.expressions[
            "cumulative_emissions_change"
        ]
        cumulative_existing = (
            model_constructor.optimization_model.parameters.carbon_emissions_cumulative_existing
        )
        rhs = (
            xr.ones_like(
                model_constructor.optimization_model.variables[
                    "carbon_emissions_cumulative"
                ].mask
            )
            * cumulative_existing
        ).where(m, 0)
        constraints = lhs == rhs

        return constraints
