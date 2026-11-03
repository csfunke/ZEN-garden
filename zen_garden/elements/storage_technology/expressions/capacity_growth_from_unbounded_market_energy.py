import pandas as pd

from zen_garden.model.component_types.expression import GenericExpression


class CapacityGrowthFromUnboundedMarketEnergy(GenericExpression):
    """Storage energy growth supported by peer technologies."""

    name = "capacity_growth_from_unbounded_market_energy"
    indices = ("set_storage_technologies", "set_nodes", "set_years")

    @classmethod
    def get_expression(cls, model_constructor):
        r"""Construct unbounded-market storage energy growth.

        Summary:
            Use capacity of peer storage technologies serving the same carrier.

        Formulation:

        .. math::

            \sum_{h'\ne h:c_{h'}^{ref}=c_h^{ref}}
            s^{market}E^{previous}_{h',n,y}

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Storage energy growth supported by peer technologies.
        """
        model = model_constructor.optimization_model
        previous = model.variables["capacity_previous_energy"]
        technologies = model.sets["set_storage_technologies"]
        shares = {
            (technology, other): (
                model.parameters.market_share_unbounded
                if other != technology
                and model.sets["set_reference_carriers"][technology][0]
                == model.sets["set_reference_carriers"][other][0]
                else 0
            )
            for technology in technologies
            for other in technologies
        }
        shares = pd.Series(shares)
        shares.index.names = [
            "set_storage_technologies",
            "set_other_storage_technologies",
        ]
        shares = shares.to_xarray().broadcast_like(previous.lower).fillna(0)
        return (
            (
                shares
                * previous.rename(
                    {"set_storage_technologies": "set_other_storage_technologies"}
                )
            )
            .where(shares != 0)
            .sum("set_other_storage_technologies")
        )
