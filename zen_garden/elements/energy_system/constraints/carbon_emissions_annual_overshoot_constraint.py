import numpy as np

from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsAnnualOvershootConstraint(GenericConstraint):
    """Carbon Emissions Annual Overshoot."""

    name = "constraint_carbon_emissions_annual_overshoot"
    indices = ("set_years",)

    @classmethod
    def should_construct(cls, model_constructor):
        model = model_constructor.optimization_model
        no_price = model.parameters.price_carbon_emissions_annual_overshoot == np.inf
        no_limit = (model.parameters.carbon_emissions_annual_limit == np.inf).all()
        return bool(no_price) != bool(no_limit)

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Enforce zero annual overshoot when exactly one disabling condition holds.

        Annual overshoot is fixed to zero when either its price is infinite or no
        finite annual emissions limit exists, provided only one condition holds.

        Formulation:

        .. math::
            \\text{if exactly one of } \\pi^{\\mathrm{CO_2,ann}} =\\infty
            \\text{ and } \\overline{m}_y=\\infty\\;\\forall y
            \\text{, then: } M_y^{\\mathrm{ann,over}} = 0

        Notation:

        :math:`M_y^{\\mathrm{ann,over}}`: overshoot of the annual carbon emissions limit
        of energy system
        :math:`\\pi^{\\mathrm{CO_2,ann}}`: carbon price for annual overshoot
        :math:`\\overline{m}_y`: annual carbon emissions limit

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Constraint over its declared model indices.
        """
        return (
            model_constructor.optimization_model.variables[
                "carbon_emissions_annual_overshoot"
            ]
            == 0
        )
