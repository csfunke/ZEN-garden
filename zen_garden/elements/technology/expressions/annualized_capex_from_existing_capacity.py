"""Annualized CAPEX attributable to existing capacity."""

from zen_garden.model.component_types.expression import GenericExpression


class AnnualizedCapexFromExistingCapacity(GenericExpression):
    """Annualize remaining overnight CAPEX of existing capacity."""

    name = "annualized_capex_from_existing_capacity"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        discount_rate = optimization_model.parameters.discount_rate
        depreciation_time = optimization_model.parameters.depreciation_time
        annuity = (
            ((1 + discount_rate) ** depreciation_time * discount_rate)
            / ((1 + discount_rate) ** depreciation_time - 1)
            if discount_rate != 0
            else 1 / depreciation_time
        )
        return annuity * optimization_model.parameters.existing_capex
