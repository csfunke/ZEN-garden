import xarray as xr

from zen_garden.elements.storage_technology.masks._utils import canonical_storage_array
from zen_garden.elements.technology.masks._utils import year_offset
from zen_garden.model.component_types.mask import GenericMask


class EnergyCapacityAdditionEligibleMask(GenericMask):
    """Storage energy additions that may be completed in the modeled horizon."""

    name = "energy_capacity_addition_eligible"
    indices = ("set_technologies", "set_location", "set_years")

    @classmethod
    def get_mask(cls, model_constructor, registry):
        model = model_constructor.optimization_model
        existing = canonical_storage_array(
            model.parameters.existing_capacities_energy.fillna(0)
        )
        limit = canonical_storage_array(model.parameters.capacity_limit_energy)
        eligible = limit.notnull() & (limit > existing)
        if not model_constructor.config.system.allow_investment:
            return xr.zeros_like(eligible, dtype=bool)

        years = list(model.sets["set_years"])
        existing_investment = canonical_storage_array(
            model.parameters.capacity_investment_existing_energy
        )
        for technology in model.sets["set_storage_technologies"]:
            delay = year_offset(
                model_constructor, technology, "construction_time", ceil=True
            )
            for completion_year in years:
                investment_year = completion_year - delay
                if investment_year in years:
                    continue
                existing_years = existing_investment.coords.get(
                    "set_years_entire_horizon"
                )
                if existing_years is None or investment_year not in existing_years:
                    eligible.loc[technology, :, completion_year] = False
                    continue
                committed = (
                    existing_investment.sel(
                        set_technologies=technology,
                        set_years_entire_horizon=investment_year,
                    ).fillna(0)
                    != 0
                )
                eligible.loc[technology, :, completion_year] &= committed
        return eligible.fillna(False)
