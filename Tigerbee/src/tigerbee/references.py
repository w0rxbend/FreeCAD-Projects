"""User-confirmed nominal design dimensions and preserved historical measurements."""

NOMINAL_WHEELBASE_MM = 305.0
ARM_THICKNESS_MM = 5.0
PLATE_THICKNESS_MM = 3.0
STANDOFF_DIAMETER_MM = 6.0
# The user's latest nominal design supersedes the approximate original reading;
# retain the reading below as historical evidence, not the manufacturing target.

MEASURED_WHEELBASE_RANGE_MM = (303.0, 304.0)
# Working allowance for the user's approximate millimeter-level reading.
# This is not a confirmed instrument accuracy or a manufacturing tolerance.
WHEELBASE_COMPARISON_ALLOWANCE_MM = 0.5
MEASUREMENT_REFERENCE = "refs/measurements.md"


def wheelbase_matches_measurement(diagonals: list[float]) -> bool:
    lower, upper = MEASURED_WHEELBASE_RANGE_MM
    allowance = WHEELBASE_COMPARISON_ALLOWANCE_MM
    return len(diagonals) == 2 and all(
        lower - allowance <= value <= upper + allowance for value in diagonals
    )


def wheelbase_matches_nominal(diagonals: list[float], tolerance: float = 1e-6) -> bool:
    """Compare both diagonals with the explicit 305 mm design target."""
    return len(diagonals) == 2 and all(
        abs(value - NOMINAL_WHEELBASE_MM) <= tolerance for value in diagonals
    )
