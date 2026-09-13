"""Physical measurements take precedence over dimensions printed on product photos."""

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
