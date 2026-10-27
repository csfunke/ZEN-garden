"""Beyond-horizon investment constraint."""

from zen_garden.model.component_types.constraint import GenericConstraint


class TechnologyConstructionTimeOutsideConstraint(GenericConstraint):
    """Prevent investments that commission only after the modeled horizon."""

    name = "constraint_technology_construction_time_outside"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_time_steps_construction",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        """Return whether any modeled investment lies beyond the horizon."""
        expression = model_constructor.optimization_model.expressions[
            "investments_beyond_horizon"
        ]
        return bool((expression.labels >= 0).any())

    @classmethod
    def get_constraint(cls, model_constructor):
        return (
            model_constructor.optimization_model.expressions[
                "investments_beyond_horizon"
            ]
            == 0
        )
