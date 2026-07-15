"""Managed, headless Python CAD build tools."""

from .context import BuildContext
from .elements import (
    DesignElement,
    DesignModel,
    Dimensions,
    IfcMapping,
    MaterialSpec,
    Placement,
    QuantityRecord,
    ValidationIssue,
)

__all__ = [
    "BuildContext",
    "DesignElement",
    "DesignModel",
    "Dimensions",
    "IfcMapping",
    "MaterialSpec",
    "Placement",
    "QuantityRecord",
    "ValidationIssue",
]

__version__ = "1.0.0"
