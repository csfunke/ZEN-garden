import numpy as np

from zen_garden.elements.technology.diffusion import (
    diffusion_rate,
    technology_location_mask,
)
from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.model.linear_expression import align_and_mask


class TechnologyDiffusionLimitTotalConstraint(GenericConstraint):
    """Limit aggregate additions without counting cross-location spillovers twice."""

    name = "constraint_technology_diffusion_limit_total"
    indices = ("set_technologies", "set_capacity_types", "set_years")

    @classmethod
    def should_construct(cls, model_constructor):
        return bool((diffusion_rate(model_constructor) != np.inf).any().item())

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        additions = model.variables["capacity_addition"]
        lhs = (
            additions
            - model.expressions["capacity_growth_from_local_learning"]
            - model.expressions["capacity_growth_from_unbounded_market"]
        ).sum("set_location")
        free_growth = model.parameters.capacity_addition_unbounded.broadcast_like(
            diffusion_rate(model_constructor)
        ).where(technology_location_mask(model_constructor), 0)
        rhs = (
            model.expressions["capacity_growth_from_existing_capacity"] + free_growth
        ).sum("set_location")
        rhs = rhs.broadcast_like(lhs.const)
        mask = diffusion_rate(model_constructor).sum("set_location") != np.inf
        return align_and_mask(lhs, mask) <= align_and_mask(rhs, mask)
