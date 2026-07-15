"""Compatibility namespace; FreeCAD is invoked only by the optional FCStd exporter."""

from ..exporters.fcstd import FcstdExporter

__all__ = ["FcstdExporter"]
