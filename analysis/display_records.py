"""
display_records.py
------------------
Display records from a CSV or Parquet file.
File format is detected automatically from the file extension.

Usage:
    # Display all records
    python analysis/display_records.py --file ./data/sales_001.csv
    python analysis/display_records.py --file ./cleaned/sales_001.parquet

    # Display first N records
    python analysis/display_records.py --file ./data/sales_001.csv --n 10
    python analysis/display_records.py --file ./cleaned/sales_001.parquet --n 5
"""

import argparse
import os

import pandas as pd


# ── Loader ────────────────────────────────────────────────────────────────────

def load_file(path: str) -> pd.DataFrame:
    """Load a CSV or Parquet file based on file extension."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".parquet":
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Use .csv or .parquet")

    return df


# ── Display ───────────────────────────────────────────────────────────────────

def display(df: pd.DataFrame, n: int | None) -> None:
    """Print file info and records."""
    subset = df if n is None else df.head(n)
    label = "all" if n is None else str(n)

    print(f"  Rows in file : {len(df):,}")
    print(f"  Columns      : {len(df.columns)}")
    print(f"  Displaying   : {label} record(s)")
    print()

    # Widen pandas display so columns don't get truncated
    with pd.option_context(
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", None,
        "display.max_colwidth", 30,
    ):
        print(subset.to_string(index=True))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Display records from a CSV or Parquet file"
    )
    parser.add_argument(
        "--file", type=str, required=True,
        help="Path to a .csv or .parquet file"
    )
    parser.add_argument(
        "--n", type=int, default=None,
        help="Number of records to display (default: all)"
    )
    args = parser.parse_args()

    df = load_file(args.file)

    print("=" * 60)
    print(f"FILE : {args.file}")
    print("=" * 60)
    display(df, args.n)
    print()


if __name__ == "__main__":
    main()
