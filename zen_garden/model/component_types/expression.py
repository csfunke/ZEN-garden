"""Generic linear-expression class for OptimizationModel."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from zen_garden.model.linear_expression import validate_component_indices

if TYPE_CHECKING:
    from zen_garden.model.constructor import ModelConstructor


class GenericExpression(ABC):
    """Base class for reusable linear expressions.

    An expression is a named piece of a constraint or objective -- a linopy
    ``LinearExpression`` (or ``xarray.DataArray``) built from variables and
    parameters during model construction, after the variables and before the
    constraints. :meth:`build` registers it on the optimization model via
    ``optimization_model.add_expression``; it is then reused elsewhere through
    ``optimization_model.expressions[<name>]``. Concrete expressions document
    their public indices (excluding Linopy's internal ``_term`` dimension) and
    named dependencies as immutable class metadata.
    """

    name: ClassVar[str]
    doc: ClassVar[str] = ""
    indices: ClassVar[tuple[str, ...]]
    dependencies: ClassVar[tuple[str, ...]] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "name" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define 'name'")
        if "indices" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define 'indices'")
        if not isinstance(cls.indices, tuple):
            raise TypeError(f"{cls.__name__}.indices must be a tuple")
        if not isinstance(cls.dependencies, tuple):
            raise TypeError(f"{cls.__name__}.dependencies must be a tuple")

    @classmethod
    def build(cls, model_constructor: "ModelConstructor") -> None:
        """Compute the expression and register it on the optimization model."""
        if not cls.should_construct(model_constructor):
            return
        expression = cls.get_expression(model_constructor)
        validate_component_indices(cls.name, cls.indices, expression)
        model_constructor.optimization_model.add_expression(cls.name, expression)

    @classmethod
    @abstractmethod
    def get_expression(cls, model_constructor: "ModelConstructor") -> Any:
        """Return the linear expression built from variables and parameters."""

    @classmethod
    def should_construct(cls, model_constructor: "ModelConstructor") -> bool:
        """Return whether this expression is needed by the current configuration."""
        return True

    @classmethod
    def construction_order(
        cls, expressions: list[type["GenericExpression"]]
    ) -> list[type["GenericExpression"]]:
        """Return expression specifications in dependency order."""
        expressions_by_name: dict[str, type[GenericExpression]] = {}
        for expression in expressions:
            existing = expressions_by_name.get(expression.name)
            if existing is not None:
                raise ValueError(
                    f"Multiple expression specifications define {expression.name!r}: "
                    f"{existing.__name__} and {expression.__name__}"
                )
            expressions_by_name[expression.name] = expression

        all_names = set(expressions_by_name)
        for expression in expressions_by_name.values():
            missing = set(expression.dependencies).difference(all_names)
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(
                    f"Expression {expression.name!r} has unknown dependencies: "
                    f"{names}"
                )

        remaining = list(expressions_by_name.values())
        completed: set[str] = set()
        ordered: list[type[GenericExpression]] = []
        while remaining:
            ready = [
                expression
                for expression in remaining
                if set(expression.dependencies).issubset(completed)
            ]
            if not ready:
                cycle = ", ".join(expression.name for expression in remaining)
                raise ValueError(f"Cyclic expression dependencies: {cycle}")
            for expression in ready:
                remaining.remove(expression)
                ordered.append(expression)
                completed.add(expression.name)
        return ordered
