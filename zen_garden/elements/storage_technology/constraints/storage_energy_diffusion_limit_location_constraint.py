import numpy as np

from zen_garden.elements.technology.diffusion import storage_energy_diffusion_rate
from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.model.linear_expression import align_and_mask


class StorageEnergyDiffusionLimitLocationConstraint(GenericConstraint):
    """Limit storage energy additions at each node using market knowledge."""

    name = "constraint_storage_energy_diffusion_limit"
    indices = ("set_storage_technologies", "set_nodes", "set_years")

    @classmethod
    def should_construct(cls, model_constructor):
        model = model_constructor.optimization_model
        return model.parameters.knowledge_spillover_rate != np.inf and bool(
            (storage_energy_diffusion_rate(model_constructor) != np.inf).any().item()
        )

    @classmethod
    def get_constraint(cls, model_constructor):
        r"""Construct the nodal storage energy diffusion limit.

        Summary:
            Limit energy additions at each node using local and shared knowledge.

        Formulation:

        .. math::

            \Delta E_{h,n,y}\leq d_{h,n,y}e^{knowledge,spill}_{h,n,y}
            +E^{peer}_{h,n,y}+e^{unbounded}_{h}

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Nodal storage energy diffusion constraint.
        """
        model = model_constructor.optimization_model
        lhs = (
            model.variables["capacity_addition_energy"]
            - model.expressions["capacity_growth_from_spillovers_energy"]
            - model.expressions["capacity_growth_from_unbounded_market_energy"]
        )
        free_growth = (
            model.parameters.capacity_addition_unbounded_energy.broadcast_like(
                storage_energy_diffusion_rate(model_constructor)
            )
        )
        rhs = (
            model.expressions[
                "capacity_growth_from_existing_capacity_with_spillovers_energy"
            ]
            + free_growth
        ).broadcast_like(lhs.const)
        mask = storage_energy_diffusion_rate(model_constructor) != np.inf
        return align_and_mask(lhs, mask) <= align_and_mask(rhs, mask)
