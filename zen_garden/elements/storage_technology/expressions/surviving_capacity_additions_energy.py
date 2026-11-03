"""Storage energy-capacity additions that remain within their lifetime."""

import itertools

import pandas as pd

from zen_garden.elements.technology.lifetime import get_active_vintage_years
from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.linear_expression import transpose_linear_expression


class SurvivingCapacityAdditionsEnergy(GenericExpression):
    """Sum storage energy-capacity vintages that have not retired."""

    name = "surviving_capacity_additions_energy"
    indices = ("set_storage_technologies", "set_nodes", "set_years")

    @classmethod
    def get_expression(cls, model_constructor):
        r"""Construct surviving storage energy-capacity additions.

        Summary:
            Sum modeled energy-capacity additions that remain available.

        Formulation:

        .. math::

            \sum_{v\in\mathcal V^{active}_{h,y}}\Delta E_{h,n,v}

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Available modeled storage energy capacity.
        """
        model = model_constructor.optimization_model
        capacity = model.variables["capacity_energy"]
        active_vintages = pd.MultiIndex.from_tuples(
            [
                (technology, year, vintage)
                for technology, year in itertools.product(
                    model.sets["set_storage_technologies"],
                    model.sets["set_years"],
                )
                for vintage in get_active_vintage_years(
                    model_constructor, technology, year
                )
            ],
            names=["set_storage_technologies", "set_years", "set_years_prev"],
        )
        active = pd.Series(1, index=active_vintages).to_xarray()
        active = active.broadcast_like(capacity.lower).fillna(0)
        active = active.transpose(*capacity.dims, "set_years_prev")
        additions = model.variables["capacity_addition_energy"].rename(
            {"set_years": "set_years_prev"}
        )
        additions = transpose_linear_expression(
            1 * additions.broadcast_like(active), active.dims
        )
        return (active * additions).sum("set_years_prev")
