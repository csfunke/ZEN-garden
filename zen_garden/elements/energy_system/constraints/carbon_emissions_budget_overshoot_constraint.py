import numpy as np

from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsBudgetOvershootConstraint(GenericConstraint):
    name = "constraint_carbon_emissions_budget_overshoot"
    indices = ("set_years",)

    @classmethod
    def should_construct(cls, model_constructor):
        return (
            model_constructor.optimization_model.parameters.price_carbon_emissions_budget_overshoot
            == np.inf
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Enforces zero budget overshoot if price for budget overshoot is inf.

        ensures carbon emissions overshoot of carbon budget is zero when
        carbon emissions price for budget overshoot is inf.

        Formulation:

        .. math::
            \\text{if } \\pi^{\\mathrm{CO_2,bud}} =\\infty
            \\text{, then: }M_y^{\\mathrm{bud,over}} = 0

        Notation:

        :math:`M_y^{\\mathrm{bud,over}}`: overshoot carbon emissions of energy system at
        the end of the time horizon
        :math:`\\pi^{\\mathrm{CO_2,bud}}`: carbon price for budget overshoot
        """
        return (
            model_constructor.optimization_model.variables[
                "carbon_emissions_budget_overshoot"
            ]
            == 0
        )
