class ArchQEDError(RuntimeError):
    """Base error with a stable CLI exit code."""
    exit_code = 2


class DriftError(ArchQEDError):
    exit_code = 3


class GateError(ArchQEDError):
    exit_code = 4


class VerificationError(ArchQEDError):
    exit_code = 5
