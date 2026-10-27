import xarray as xr

from zen_garden.model.component_types.constraint import GenericConstraint


class NodalEnergyBalanceConstraint(GenericConstraint):
    """Balance net carrier supply and demand at every node and time step."""

    name = "constraint_nodal_energy_balance"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        net_supply = model.expressions["nodal_net_supply"]
        demand = model.parameters.demand
        aligned_coordinates = xr.align(net_supply.coords, demand, join="inner")[0]
        return net_supply.sel(aligned_coordinates) == demand.sel(aligned_coordinates)
