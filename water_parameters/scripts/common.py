"""Shared paths and helpers for building the i-CLEANED hosted water parameter tables."""
import os
from pathlib import Path

# Raw downloads live outside the repository (large files); set ICLEANED_WATER_RAW to override.
RAW = Path(os.environ.get(
    "ICLEANED_WATER_RAW",
    "/tmp/claude-0/-home-user-CLEANED/510c690a-c57f-5b28-bfb0-abbad02a847d/scratchpad/data",
))
REPO = Path(__file__).resolve().parents[1]
TABLES = REPO / "tables"
ADMIN1 = RAW / "admin1_global_south.gpkg"

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MID_MONTH_DOY = [15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]


def peff_usda_scs(p_mm_month):
    """USDA-SCS effective rainfall (monthly, mm) as implemented in FAO CROPWAT (Smith 1992)."""
    import numpy as np
    p = np.asarray(p_mm_month, dtype="float64")
    return np.where(p <= 250.0, p * (125.0 - 0.2 * p) / 125.0, 125.0 + 0.1 * p)
