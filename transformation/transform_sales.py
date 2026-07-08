"""
transform_sales.py
------------------
Cleans and transforms raw sales CSVs into analysis-ready output.

Transformations applied:
  1. Drop cancelled orders
  2. Normalize string columns (strip whitespace)
  3. Add revenue_tier column (Low / Medium / High)
  4. Add is_discounted boolean column
  5. Add day_of_week, quarter, and month columns
  6. Write cleaned data to ./cleaned/<same-filename>.parquet

The output filename mirrors the input filename with a .parquet extension.
When the input is a directory, the output file is named sales_clean.parquet.

Usage:
    # Single file — outputs ./cleaned/sales_001.parquet
    python transformation/transform_sales.py --input ./data/sales_001.csv

    # Directory — outputs ./cleaned/sales_clean.parquet
    python transformation/transform_sales.py --input ./data/

    # Custom output folder
    python transformation/transform_sales.py --input ./data/ --output-dir ./processed/
"""

import argparse
import glob
import os
import warnings

import pandas as pd

# pandas 2.2 emits ChainedAssignmentError FutureWarnings even when mutations
# are safe (e.g., after df.copy()). Suppress them with message matching.
warnings.filterwarnings("ignore", message="ChainedAssignment", category=FutureWarning)


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "sales_*.csv"))
        # Exclude already-processed files
        files = [f for f in files if "clean" not in f and "summary" not in f]
        if not files:
            raise FileNotFoundError(f"No raw sales_*.csv files found in {path}")
        df = pd.concat([pd.read_csv(f) for f in sorted(files)], ignore_index=True)
        print(f"Loaded {len(files)} file(s) → {len(df)} total records")
    else:
        df = pd.read_csv(path)
        print(f"Loaded {len(df)} records from {path}")
    return df


# ── Transformations ───────────────────────────────────────────────────────────

def drop_cancelled(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    # Boolean indexing + reset_index gives an independent DataFrame (not a view)
    df = df[df["status"] != "Cancelled"].reset_index(drop=True)
    print(f"  drop_cancelled     : {before - len(df)} rows removed → {len(df)} remain")
    return df


def normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    # .copy() ensures this is an independent DataFrame before mutating columns
    df = df.copy()
    df["city"] = df["city"].str.strip()
    df["category"] = df["category"].str.strip()
    df["product_name"] = df["product_name"].str.strip()
    df["sales_channel"] = df["sales_channel"].str.strip()
    df["payment_method"] = df["payment_method"].str.strip()
    print("  normalize_strings  : done")
    return df


def add_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["day_of_week"] = df["sale_date"].dt.day_name()
    df["quarter"] = df["sale_date"].dt.quarter.map(lambda q: f"Q{q}")
    df["month"] = df["sale_date"].dt.to_period("M").astype(str)
    print("  add_date_columns   : day_of_week, quarter, month added")
    return df


def add_revenue_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tier thresholds (VND):
      Low    < 1,000,000
      Medium  1,000,000 – 9,999,999
      High   ≥ 10,000,000
    """
    df = df.copy()
    bins = [0, 1_000_000, 10_000_000, float("inf")]
    labels = ["Low", "Medium", "High"]
    df["revenue_tier"] = pd.cut(
        df["total_amount"], bins=bins, labels=labels, right=False
    )
    print("  add_revenue_tier   : Low / Medium / High")
    return df


def add_is_discounted(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_discounted"] = df["discount_pct"] > 0
    print("  add_is_discounted  : boolean column added")
    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    preferred = [
        "order_id", "sale_date", "month", "quarter", "day_of_week",
        "sale_time", "product_name", "category",
        "unit_price", "quantity", "discount_pct", "discount_amount",
        "total_amount", "revenue_tier", "is_discounted",
        "city", "sales_channel", "payment_method", "status", "sales_rep_id",
    ]
    existing = [c for c in preferred if c in df.columns]
    extras = [c for c in df.columns if c not in existing]
    return df[existing + extras]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Transform raw sales CSV data")
    parser.add_argument(
        "--input", type=str, default="./data/",
        help="Path to raw CSV file or directory (default: ./data/)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./cleaned/",
        help="Output folder for cleaned Parquet files (default: ./cleaned/)"
    )
    args = parser.parse_args()

    # Derive output filename from input:
    #   single file  → same stem with .parquet  (e.g. sales_001.csv → sales_001.parquet)
    #   directory    → sales_clean.parquet
    if os.path.isdir(args.input):
        out_filename = "sales_clean.parquet"
    else:
        stem = os.path.splitext(os.path.basename(args.input))[0]
        out_filename = f"{stem}.parquet"

    output_path = os.path.join(args.output_dir, out_filename)

    print("Loading data...")
    df = load_data(args.input)

    print("\nApplying transformations:")
    df = drop_cancelled(df)
    df = normalize_strings(df)
    df = add_date_columns(df)
    df = add_revenue_tier(df)
    df = add_is_discounted(df)
    df = reorder_columns(df)

    # Write cleaned data as Parquet
    os.makedirs(os.path.abspath(args.output_dir), exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"\n✓ Cleaned data → {output_path}  ({len(df)} rows)")

    print("\nDone.")


if __name__ == "__main__":
    main()
