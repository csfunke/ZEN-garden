import linopy as lp
import xarray as xr
from linopy.expressions import LinearExpression

from zen_garden.elements.storage_technology.masks import EnergyCapacityAvailableMask
from zen_garden.model.component_types.constraint import GenericConstraint


class StorageEnergyLifetimePreviousConstraint(GenericConstraint):
    """Define storage energy capacity before current-year additions."""

    name = "constraint_storage_energy_lifetime_previous"
    indices = ("set_storage_technologies", "set_nodes", "set_years")
    masks = (EnergyCapacityAvailableMask,)

    @classmethod
    def get_constraint(cls, model_constructor):
        r"""Construct beginning-of-year storage energy capacity.

        Summary:
            Exclude current-year additions from available storage energy capacity.

        Formulation:

        .. math::

            E^{previous}_{h,n,y}=e^{existing}_{h,n,y}
            +\sum_{v\in\mathcal V^{active}_{h,y}}\Delta E_{h,n,v}
            -\Delta E_{h,n,y}

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Beginning-of-year storage energy-capacity constraint.
        """
        model = model_constructor.optimization_model
        lhs = lp.merge(
            [
                1 * model.variables["capacity_previous_energy"],
                -model.expressions["surviving_capacity_additions_energy"],
                1 * model.variables["capacity_addition_energy"],
            ],
            compat="broadcast_equals",
            join="outer",
            cls=LinearExpression,
        )
        rhs = xr.align(
            lhs.const, model.parameters.existing_capacities_energy, join="left"
        )[1]
        return lhs == rhs
