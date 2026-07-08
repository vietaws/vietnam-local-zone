"""
display_records.py
------------------
Display records from a CSV or Parquet file.
File format is detected automatically from the file extension.

String values are shown with surrounding quotes so leading/trailing
spaces are immediately visible — making it easy to compare raw CSV
(before transformation) against cleaned Parquet (after transformation).

Usage:
    # Display all records
    python analysis/display_records.py --file ./data/sales_001.csv
    python analysis/display_records.py --file ./cleaned/sales_001.parquet

    # Display first N records
    python analysis/display_records.py --file ./data/sales_001.csv --n 10
    python analysis/display_records.py --file ./cleaned/sales_001.parquet --n 5

    # Check which columns contain leading/trailing spaces
    python analysis/display_records.py --file ./data/sales_001.csv --check-spaces
    python analysis/display_records.py --file ./cleaned/sales_001.parquet --check-spaces
"""

import argparse
import os
from typing import Optional

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

def display(df: pd.DataFrame, n: Optional[int]) -> None:
    """
    Print records with string columns quoted so spaces are visible.

    e.g. a product name with 4 leading spaces appears as:
         '    Bàn làm việc gỗ'   ← spaces clearly visible
    instead of:
             Bàn làm việc gỗ     ← spaces invisible
    """
    subset = df if n is None else df.head(n)
    label = "all" if n is None else str(n)

    print(f"  Rows in file : {len(df):,}")
    print(f"  Columns      : {len(df.columns)}")
    print(f"  Displaying   : {label} record(s)")
    print(f"  Note         : string values are quoted — spaces inside quotes are real")
    print()

    # Build a display copy where every string cell is wrapped in single quotes
    # so leading/trailing whitespace is unmistakably visible in the output.
    display_df = subset.copy()
    for col in display_df.select_dtypes(include="object").columns:
        display_df.loc[:, col] = display_df[col].apply(
            lambda v: f"'{v}'" if pd.notna(v) else v
        )

    with pd.option_context(
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", None,
        "display.max_colwidth", 40,
    ):
        print(display_df.to_string(index=True))


# ── Space checker ─────────────────────────────────────────────────────────────

def check_spaces(df: pd.DataFrame) -> None:
    """Report every string column that contains values with leading/trailing spaces."""
    print("\n" + "=" * 60)
    print("WHITESPACE CHECK — STRING COLUMNS")
    print("=" * 60)

    string_cols = df.select_dtypes(include="object").columns.tolist()
    found_any = False

    for col in string_cols:
        dirty = df[col].dropna()
        dirty = dirty[dirty != dirty.str.strip()]
        if dirty.empty:
            print(f"  ✓  {col}")
        else:
            found_any = True
            print(f"  ✗  {col}  ({len(dirty)} dirty value(s))")
            for val in dirty.unique():
                leading  = len(val) - len(val.lstrip())
                trailing = len(val) - len(val.rstrip())
                detail = []
                if leading:
                    detail.append(f"{leading} leading")
                if trailing:
                    detail.append(f"{trailing} trailing")
                print(f"       raw  : {repr(val)}")
                print(f"       clean: {repr(val.strip())}  [{', '.join(detail)} space(s)]")

    if not found_any:
        print("\n  All string columns are clean — no leading/trailing spaces found.")


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
    parser.add_argument(
        "--check-spaces", action="store_true",
        help="Report columns with leading/trailing whitespace in string values"
    )
    args = parser.parse_args()

    df = load_file(args.file)

    print("=" * 60)
    print(f"FILE : {args.file}")
    print("=" * 60)

    if args.check_spaces:
        check_spaces(df)
    else:
        display(df, args.n)

    print()


if __name__ == "__main__":
    main()
