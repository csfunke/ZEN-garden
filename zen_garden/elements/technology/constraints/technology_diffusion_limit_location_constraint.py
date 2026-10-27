import numpy as np

from zen_garden.elements.technology.diffusion import (
    diffusion_rate,
    technology_location_mask,
)
from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.model.linear_expression import align_and_mask


class TechnologyDiffusionLimitLocationConstraint(GenericConstraint):
    """Limit additions at each location using available installation knowledge."""

    name = "constraint_technology_diffusion_limit"
    indices = (
        "set_technologies",
        "set_capacity_types",
        "set_location",
        "set_years",
    )

    @classmethod
    def should_construct(cls, model_constructor):
        model = model_constructor.optimization_model
        return model.parameters.knowledge_spillover_rate != np.inf and bool(
            (diffusion_rate(model_constructor) != np.inf).any().item()
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        lhs = (
            model.variables["capacity_addition"]
            - model.expressions["capacity_growth_from_spillovers"]
            - model.expressions["capacity_growth_from_unbounded_market"]
        )
        free_growth = model.parameters.capacity_addition_unbounded.broadcast_like(
            diffusion_rate(model_constructor)
        ).where(technology_location_mask(model_constructor), 0)
        rhs = (
            model.expressions["capacity_growth_from_existing_capacity_with_spillovers"]
            + free_growth
        ).broadcast_like(lhs.const)
        mask = diffusion_rate(model_constructor) != np.inf
        return align_and_mask(lhs, mask) <= align_and_mask(rhs, mask)
