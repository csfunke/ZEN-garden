"""Nodal carrier consumption by conversion technologies."""

import linopy as lp
from linopy.expressions import LinearExpression

from zen_garden.model.component_types.expression import GenericExpression
from zen_garden.model.registries.multi_index_helper import MultiIndexHelper


class NodalConversionConsumption(GenericExpression):
    """Aggregate conversion input flow by carrier and node."""

    name = "nodal_conversion_consumption"
    indices = (
        "set_carriers",
        "set_nodes",
        "set_years",
        "set_representative_hours",
    )

    @classmethod
    def get_expression(cls, model_constructor):
        """Construct aggregate conversion input flow by carrier and node.

        Summary:
            Aggregate conversion input flow by carrier and node.

        Formulation:

        .. math::

            \\sum_{h:c\\in\\mathcal C_h^{in}}F^{in}_{h,c,n,y,r}

        The formulation applies over valid combinations of the declared indices.
        Empty or masked combinations are not constructed.

        Notation:
            Symbols and indices follow ``sets_params_constraints.rst``.

        Args:
            model_constructor: Object containing the optimization model.

        Returns:
            Expression over its declared model indices.
        """
        optimization_model = model_constructor.optimization_model
        index_values, index_names = optimization_model.create_custom_set(
            ["set_carriers", "set_nodes", "set_years", "set_representative_hours"]
        )
        index = MultiIndexHelper(index_values, index_names)
        flows = []
        nodes = list(optimization_model.sets["set_nodes"])
        for carrier in index.get_unique([0]):
            technologies = [
                technology
                for technology in optimization_model.sets["set_conversion_technologies"]
                if carrier in optimization_model.sets["set_input_carriers"][technology]
            ]
            selected_carrier = [carrier] if technologies else []
            variable = optimization_model.variables["flow_conversion_input"]
            flows.append(
                variable.loc[technologies, selected_carrier, nodes].sum(
                    variable.dims[:2]
                )
            )
        merged = lp.merge(flows, dim="group", join="outer", cls=LinearExpression)
        return optimization_model.constraints.reorder_group(
            merged,
            None,
            None,
            index.get_unique([0]),
            index_names[:1],
            optimization_model.lp_model,
        )
