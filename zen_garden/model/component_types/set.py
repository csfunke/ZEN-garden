"""Declarative model-set specifications."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, final

from zen_garden.model.component_types.component import GenericComponent
from zen_garden.model.component_types.index import GenericIndex

if TYPE_CHECKING:
    from zen_garden.model.constructor import ModelConstructor


class GenericSet(GenericComponent, ABC):
    """Base class for model sets constructed from schema specifications."""

    name: ClassVar[str]
    symbol: ClassVar[str]
    doc: ClassVar[str]
    index_set: ClassVar[type[GenericSet] | type[GenericIndex] | None] = None
    _abstract_component = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("_abstract_component", False):
            return
        symbol = cls.__dict__.get("symbol")
        if not isinstance(symbol, str) or not symbol.strip():
            raise TypeError(f"{cls.__name__}.symbol must be a non-empty string")
        if cls.index_set is not None and not (
            isinstance(cls.index_set, type)
            and issubclass(cls.index_set, (GenericSet, GenericIndex))
        ):
            raise TypeError(
                f"{cls.__name__}.index_set must be a GenericSet or GenericIndex class"
            )
        if "build" in cls.__dict__:
            raise TypeError(f"{cls.__name__} must not override GenericSet.build()")

    @classmethod
    @abstractmethod
    def get_data(cls, model_constructor: "ModelConstructor") -> Any:
        """Extract the members of this set from model-construction state."""

    @classmethod
    @final
    def build(cls, model_constructor: "ModelConstructor") -> None:
        """Extract and register this set on the optimization model."""
        model_constructor.optimization_model.add_set(
            name=cls.name,
            data=cls.get_data(model_constructor),
            doc=cls.doc,
            index_set=cls.index_set.name if cls.index_set is not None else None,
        )
