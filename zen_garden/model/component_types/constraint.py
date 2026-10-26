"""Generic constraint class for OptimizationModel."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, cast

import pandas as pd
import xarray as xr
from linopy import Variable, merge
from linopy.expressions import LinearExpression

from zen_garden.model.registries.set import IndexedSet

if TYPE_CHECKING:
    from zen_garden.model.component_types.mask import GenericMask
    from zen_garden.model.constructor import ModelConstructor


class GenericConstraint(ABC):
    """Base class for constraints.

    Constraints are stateless: :meth:`build` is a classmethod that takes the
    :class:`~zen_garden.model.constructor.ModelConstructor` and adds the
    constraint's rows to the optimization model. The helper methods below are
    stateless too.
    """

    masks: ClassVar[dict[str, list[type["GenericMask"]]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        inherited_masks = {}
        for base in cls.__bases__:
            inherited_masks.update(getattr(base, "masks", {}))
        own_masks = cls.__dict__.get("masks", {})
        cls.masks = {**inherited_masks, **own_masks}

    @classmethod
    @abstractmethod
    def build(cls, model_constructor: "ModelConstructor") -> None:
        """Build the constraint(s) and add them to the optimization model."""

    @classmethod
    def add_constraint(cls, model_constructor, name, constraint, doc=""):
        """Add a constraint with the structural masks declared for ``name``."""
        optimization_model = model_constructor.optimization_model
        mask = optimization_model.masks.combine_for_constraint(
            cls.masks.get(name, []), constraint
        )
        if mask is not None:
            optimization_model.masks.log_reduction(name, mask)
        optimization_model.add_constraint(name, constraint, doc=doc, mask=mask)

    @staticmethod
    def get_previous_storage_time_step_array(model_constructor: "ModelConstructor"):
        """Return predecessor year/hour arrays and the valid-coupling mask."""
        optimization_model = model_constructor.optimization_model
        time_steps = model_constructor.time_steps
        previous = time_steps.previous_storage_time_step
        coupling = time_steps.storage_coupling_mask
        assert previous is not None
        assert coupling is not None
        years = list(optimization_model.sets["set_years"])
        storage_hours = list(
            optimization_model.sets[
                "set_representative_hours_storage"
            ].coordinate_values
        )
        previous_year = xr.DataArray(
            [[year for _ in storage_hours] for year in years],
            coords={
                "set_years": years,
                "set_representative_hours_storage": storage_hours,
            },
            dims=("set_years", "set_representative_hours_storage"),
        )
        previous_hour = xr.DataArray(
            [storage_hours for _ in years],
            coords=previous_year.coords,
            dims=previous_year.dims,
        )
        mask = xr.full_like(previous_year, False, dtype=bool)
        selected_years = set(years)
        previous_steps = cast(
            dict[tuple[int, int], tuple[int, int]], previous.to_dict()
        )
        coupling_values = cast(dict[tuple[int, int], bool], coupling.to_dict())
        for pair, predecessor in previous_steps.items():
            year, storage_hour = pair
            if year not in selected_years:
                continue
            predecessor_year, predecessor_hour = predecessor
            if predecessor_year not in selected_years:
                valid_hours = time_steps.representative_hours_storage
                assert valid_hours is not None
                predecessor_year = year
                predecessor_hour = valid_hours[year][-1]
            previous_year.loc[year, storage_hour] = predecessor_year
            previous_hour.loc[year, storage_hour] = predecessor_hour
            mask.loc[year, storage_hour] = coupling_values[pair]
        return previous_year, previous_hour, mask

    @staticmethod
    def get_power2energy_time_step_array(model_constructor: "ModelConstructor"):
        """Return the operational representative selected by each storage hour."""
        mapping = model_constructor.time_steps.storage_to_operation
        assert mapping is not None
        years = list(model_constructor.optimization_model.sets["set_years"])
        return mapping.loc[mapping.index.get_level_values("set_years").isin(years)]

    @staticmethod
    def map_and_expand(array, mapping):
        """Maps and expands array.

        :param array: xarray to map and expand
        :param mapping: pd.Series with mapping values
        """
        if not isinstance(mapping, pd.Series):
            raise TypeError("Mapping must be a pandas Series")
        if isinstance(mapping.index, pd.MultiIndex):
            indexer = mapping.to_xarray()
            valid = indexer.notnull()
            safe_indexer = indexer.fillna(0).astype(int)
            return array.sel({mapping.name: safe_indexer}).where(valid)
        mapped = array.sel({mapping.name: mapping.values})
        mapped = mapped.rename({mapping.name: mapping.index.name})
        return mapped.assign_coords({mapping.index.name: mapping.index})

    @staticmethod
    def align_and_mask(expr, mask):
        """Aligns and masks expr.

        :param expr: expression to align and mask
        :param mask: mask to apply
        """
        if isinstance(expr, xr.DataArray):
            aligner = expr
        elif isinstance(expr, Variable):
            aligner = expr.lower
        else:
            aligner = expr.const
        mask = xr.align(mask, aligner, join="right")[0]
        expr = expr.where(mask)
        return expr

    @staticmethod
    def get_flow_expression_conversion(
        model_constructor: "ModelConstructor", techs, nodes, factor=None, rename=False
    ):
        """Return the flow expression for conversion technologies."""
        optimization_model = model_constructor.optimization_model
        reference_carriers = cast(
            IndexedSet, optimization_model.sets["set_reference_carriers"]
        )
        input_carriers = cast(IndexedSet, optimization_model.sets["set_input_carriers"])
        reference_flows = []
        for t in techs:
            rc = reference_carriers[t][0]
            if factor is not None:
                mult = factor.loc[t, nodes]
            else:
                mult = 1
            # TODO can we avoid the indexing here?
            if rc in input_carriers[t]:
                reference_flows.append(
                    mult
                    * optimization_model.variables["flow_conversion_input"].loc[
                        t, rc, nodes, :
                    ]
                )
            else:
                reference_flows.append(
                    mult
                    * optimization_model.variables["flow_conversion_output"].loc[
                        t, rc, nodes, :
                    ]
                )
        if rename:
            term_reference_flow = merge(
                reference_flows,
                dim="set_technologies",
                join="outer",
                coords="minimal",
                compat="override",
                cls=LinearExpression,
            ).rename({"set_nodes": "set_location"})
        else:
            term_reference_flow = merge(
                reference_flows,
                dim="set_conversion_technologies",
                join="outer",
                coords="minimal",
                compat="override",
                cls=LinearExpression,
            )
        return term_reference_flow

    @staticmethod
    def get_flow_expression_storage(model_constructor: "ModelConstructor", rename=True):
        """Return the flow expression for storage technologies."""
        optimization_model = model_constructor.optimization_model
        term = (
            optimization_model.variables["flow_storage_charge"]
            + optimization_model.variables["flow_storage_discharge"]
        )
        if rename:
            return term.rename(
                {
                    "set_storage_technologies": "set_technologies",
                    "set_nodes": "set_location",
                }
            )
        else:
            return term
