"""Typed errors raised by the managed build pipeline."""


class CadBuildError(RuntimeError):
    """Base class for actionable build failures."""


class ModelValidationError(CadBuildError):
    """The shared model violates one or more fatal invariants."""


class ExportError(CadBuildError):
    """An exporter failed to create or validate its artifact."""


class DependencyUnavailableError(CadBuildError):
    """An explicitly requested optional dependency is unavailable."""
