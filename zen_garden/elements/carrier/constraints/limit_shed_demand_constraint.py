import numpy as np

from zen_garden.model.component_types.constraint import GenericConstraint


class LimitShedDemandConstraint(GenericConstraint):
    """Limit shedding to demand, or to zero when shedding is disabled."""

    name = "constraint_limit_shed_demand"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        allowed = model.parameters.price_shed_demand != np.inf
        return model.variables["shed_demand"] <= model.parameters.demand.where(
            allowed, 0.0
        )
