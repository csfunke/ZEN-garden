from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsTechnologyTotalConstraint(GenericConstraint):
    name = "constraint_carbon_emissions_technology_total"
    indices = ("set_years",)

    @classmethod
    def get_constraint(cls, model_constructor):
        """Summary:
        Calculate total carbon emissions of each technology.

        Formulation:

        .. math::
            M_y^{\\mathrm{tech}} = \\sum_{p\\in\\mathcal{P}}
            \\sum_{t\\in\\mathcal{T}_y}\\sum_{h\\in\\mathcal{H}}
            M^{\\mathrm{tech}}_{h,p,t} \\Delta t_t

        Notation:

        :math:`M_y^{\\mathrm{tech}}`: total carbon emissions of all technologies in
        year :math:`y`
        :math:`M^{\\mathrm{tech}}_{h,p,t}`: carbon emissions of technology
        :math:`h` at location :math:`p` in time step :math:`t` of year :math:`y`
        :math:`\\Delta t_t`: duration of time step :math:`t`
        """
        model = model_constructor.optimization_model
        return (
            model.variables["carbon_emissions_technology_total"]
            == model.expressions["annual_technology_emissions"]
        )
