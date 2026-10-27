"""Nodal carrier consumption from storage charging."""

import linopy as lp
from linopy.expressions import LinearExpression

from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.registries.multi_index_helper import MultiIndexHelper


class NodalStorageCharging(GenericExpression):
    """Aggregate charging flow by storage reference carrier and node."""

    name = "nodal_storage_charging"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        optimization_model = model_constructor.optimization_model
        variable = optimization_model.variables["flow_storage_charge"]
        if variable.size == 0:
            return optimization_model.variables["flow_import"].where(False).to_linexpr()
        index_values, index_names = optimization_model.create_custom_set(
            ["set_carriers", "set_nodes", "set_years", "set_representative_hours"]
        )
        index = MultiIndexHelper(index_values, index_names)
        flows = []
        for carrier in index.get_unique([0]):
            technologies = [
                technology
                for technology in optimization_model.sets["set_storage_technologies"]
                if carrier
                in optimization_model.sets["set_reference_carriers"][technology]
            ]
            flows.append(variable.loc[technologies].sum("set_storage_technologies"))
        merged = lp.merge(flows, dim="group", join="outer", cls=LinearExpression)
        return optimization_model.constraints.reorder_group(
            merged,
            None,
            None,
            index.get_unique([0]),
            index_names[:1],
            optimization_model.lp_model,
        )
