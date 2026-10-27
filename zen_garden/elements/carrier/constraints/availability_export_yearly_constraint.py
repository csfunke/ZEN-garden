import numpy as np

from zen_garden.model.component_types.constraint import GenericConstraint


class AvailabilityExportYearlyConstraint(GenericConstraint):
    """Limit annual exports to their carrier- and node-specific availability."""

    name = "constraint_availability_export_yearly"
    indices = ("set_carriers", "set_nodes", "set_years")

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        available = model.parameters.availability_export_yearly
        mask = available != np.inf
        return model.expressions["annual_export_quantity"].where(
            mask
        ) <= available.where(mask)
