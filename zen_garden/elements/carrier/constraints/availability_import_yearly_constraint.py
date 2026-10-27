import numpy as np

from zen_garden.model.component_types.constraint import GenericConstraint


class AvailabilityImportYearlyConstraint(GenericConstraint):
    """Limit annual imports to their carrier- and node-specific availability."""

    name = "constraint_availability_import_yearly"
    indices = ("set_carriers", "set_nodes", "set_years")

    @classmethod
    def get_constraint(cls, model_constructor):
        model = model_constructor.optimization_model
        available = model.parameters.availability_import_yearly
        mask = available != np.inf
        return model.expressions["annual_import_quantity"].where(
            mask
        ) <= available.where(mask)
