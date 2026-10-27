from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsAnnualLimitConstraint(GenericConstraint):
    name = "constraint_carbon_emissions_annual_limit"
    indices = ("set_years",)

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Time dependent carbon emissions limit from technologies and carriers.

        Formulation:

        .. math::
            M_y-M_y^{\\mathrm{ann,over}}\\leq \\overline{m}_y

        Notation:

        :math:`M_y^{\\mathrm{ann,over}}`: permitted overshoot of the annual emissions
        limit
        """
        lhs = (
            model_constructor.optimization_model.variables["carbon_emissions_annual"]
            - model_constructor.optimization_model.variables[
                "carbon_emissions_annual_overshoot"
            ]
        )
        rhs = (
            model_constructor.optimization_model.parameters.carbon_emissions_annual_limit
        )
        constraints = lhs <= rhs

        return constraints
