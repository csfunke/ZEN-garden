"""Net transport inflow by carrier and node."""

import linopy as lp
import numpy as np
import xarray as xr

from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.registries.multi_index_helper import MultiIndexHelper


class NodalTransportInflow(GenericExpression):
    """Aggregate incoming transport flow after losses."""

    name = "nodal_transport_inflow"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        if optimization_model.variables["flow_transport"].size == 0:
            return optimization_model.variables["flow_import"].where(False).to_linexpr()

        index_values, index_names = optimization_model.create_custom_set(
            ["set_carriers", "set_nodes", "set_years", "set_representative_hours"]
        )
        index = MultiIndexHelper(index_values, index_names)
        connected_edges = {
            node: model_constructor.network_topology.calculate_connected_edges(
                node, "in"
            )
            for node in optimization_model.sets["set_nodes"]
        }
        max_edges = max(len(edges) for edges in connected_edges.values())
        demand = optimization_model.parameters.demand
        coords = [
            demand.coords["set_carriers"],
            demand.coords["set_nodes"],
            demand.coords["set_years"],
            demand.coords["set_representative_hours"],
            xr.DataArray(
                np.arange(
                    len(optimization_model.sets["set_transport_technologies"])
                    * (2 * max_edges + 1)
                ),
                dims=["_term"],
            ),
        ]
        shape = tuple(len(coord) for coord in coords)
        variables = np.full(shape, -1, dtype=int)
        coefficients = np.full(shape, np.nan, dtype=float)
        carrier_positions = {value: pos for pos, value in enumerate(coords[0].values)}
        node_positions = {value: pos for pos, value in enumerate(coords[1].values)}

        for carrier, node in index.get_unique([0, 1]):
            technologies = [
                technology
                for technology in optimization_model.sets["set_transport_technologies"]
                if carrier
                in optimization_model.sets["set_reference_carriers"][technology]
            ]
            edges = connected_edges[node]
            flow_labels = (
                optimization_model.variables["flow_transport"]
                .labels.loc[technologies, edges, ...]
                .data
            )
            flow_labels = flow_labels.reshape((-1, *flow_labels.shape[-2:])).transpose(
                1, 2, 0
            )
            carrier_pos = carrier_positions[carrier]
            node_pos = node_positions[node]
            count = flow_labels.shape[-1]
            variables[carrier_pos, node_pos, ..., :count] = flow_labels
            coefficients[carrier_pos, node_pos, ..., :count] = 1
            loss_labels = (
                optimization_model.variables["flow_transport_loss"]
                .labels.loc[technologies, edges, ...]
                .data
            )
            loss_labels = loss_labels.reshape((-1, *loss_labels.shape[-2:])).transpose(
                1, 2, 0
            )
            loss_count = loss_labels.shape[-1]
            variables[carrier_pos, node_pos, ..., count : count + loss_count] = (
                loss_labels
            )
            coefficients[carrier_pos, node_pos, ..., count : count + loss_count] = -1

        return lp.LinearExpression(
            xr.Dataset(
                {
                    "coeffs": xr.DataArray(coefficients, coords=coords),
                    "vars": xr.DataArray(variables, coords=coords),
                }
            ),
            optimization_model.lp_model,
        )
