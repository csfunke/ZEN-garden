"""Storage technology constraints."""

from zen_garden.model.component_types.constraint import GenericConstraint

from .capacity_energy_to_power_ratio_max_constraint import (
    CapacityEnergyToPowerRatioMaxConstraint,
)
from .capacity_energy_to_power_ratio_min_constraint import (
    CapacityEnergyToPowerRatioMinConstraint,
)
from .capacity_factor_storage_constraint import CapacityFactorStorageConstraint
from .carbon_emissions_technology_storage_constraint import (
    CarbonEmissionsTechnologyStorageConstraint,
)
from .charge_storage_binary_constraint import ChargeStorageBinaryConstraint
from .couple_storage_level_constraint import CoupleStorageLevelConstraint
from .discharge_storage_binary_constraint import DischargeStorageBinaryConstraint
from .flow_storage_spillage_constraint import FlowStorageSpillageConstraint
from .opex_technology_storage_constraint import OpexTechnologyStorageConstraint
from .storage_level_max_constraint import StorageLevelMaxConstraint
from .storage_technology_capex_constraint import StorageTechnologyCapexConstraint

STORAGE_TECHNOLOGY_CONSTRAINTS: list[type[GenericConstraint]] = [
    CapacityFactorStorageConstraint,
    OpexTechnologyStorageConstraint,
    CarbonEmissionsTechnologyStorageConstraint,
    StorageLevelMaxConstraint,
    CoupleStorageLevelConstraint,
    FlowStorageSpillageConstraint,
    CapacityEnergyToPowerRatioMinConstraint,
    CapacityEnergyToPowerRatioMaxConstraint,
    StorageTechnologyCapexConstraint,
    ChargeStorageBinaryConstraint,
    DischargeStorageBinaryConstraint,
]

__all__ = [
    "CapacityEnergyToPowerRatioMaxConstraint",
    "CapacityEnergyToPowerRatioMinConstraint",
    "CapacityFactorStorageConstraint",
    "CarbonEmissionsTechnologyStorageConstraint",
    "ChargeStorageBinaryConstraint",
    "CoupleStorageLevelConstraint",
    "FlowStorageSpillageConstraint",
    "DischargeStorageBinaryConstraint",
    "OpexTechnologyStorageConstraint",
    "StorageLevelMaxConstraint",
    "StorageTechnologyCapexConstraint",
]
