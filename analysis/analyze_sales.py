"""
analyze_sales.py
----------------
Runs simple descriptive analysis on generated sales CSV files.

Usage:
    python analysis/analyze_sales.py
    python analysis/analyze_sales.py --input ./data/sales_001.csv
    python analysis/analyze_sales.py --input ./data/  # analyse all CSVs in a folder
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
    """Load one CSV file or all CSVs in a directory."""
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found in {path}")
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
        print(f"Loaded {len(files)} file(s) → {len(df)} total records")
    else:
        df = pd.read_csv(path)
        print(f"Loaded {len(df)} records from {path}")
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Basic type casting and derived columns."""
    # Create an independent copy to avoid pandas CoW warnings
    df = df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["month"] = df["sale_date"].dt.to_period("M").astype(str)
    df["week"] = df["sale_date"].dt.isocalendar().week.astype(int)
    return df


# ── Analysis functions ────────────────────────────────────────────────────────

def summary_stats(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)
    print(f"  Total orders      : {len(df):,}")
    print(f"  Total revenue     : {df['total_amount'].sum():>20,.0f} VND")
    print(f"  Average order     : {df['total_amount'].mean():>20,.0f} VND")
    print(f"  Median order      : {df['total_amount'].median():>20,.0f} VND")
    print(f"  Max order         : {df['total_amount'].max():>20,.0f} VND")
    print(f"  Date range        : {df['sale_date'].min().date()} → {df['sale_date'].max().date()}")

    status_counts = df["status"].value_counts()
    print(f"\n  Order status breakdown:")
    for status, count in status_counts.items():
        pct = count / len(df) * 100
        print(f"    {status:<15} {count:>4} ({pct:.1f}%)")


def revenue_by_category(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("REVENUE BY CATEGORY")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("category")
        .agg(
            orders=("order_id", "count"),
            revenue=("total_amount", "sum"),
            avg_order=("total_amount", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    print(group.to_string())


def revenue_by_city(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("TOP CITIES BY REVENUE")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("city")
        .agg(revenue=("total_amount", "sum"), orders=("order_id", "count"))
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    print(group.to_string())


def revenue_by_channel(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("SALES CHANNEL PERFORMANCE")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("sales_channel")
        .agg(
            orders=("order_id", "count"),
            revenue=("total_amount", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )
    print(group.to_string())


def monthly_trend(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("MONTHLY REVENUE TREND")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("month")
        .agg(orders=("order_id", "count"), revenue=("total_amount", "sum"))
        .sort_index()
    )
    print(group.to_string())


def top_products(df: pd.DataFrame, n: int = 5) -> None:
    print("\n" + "=" * 60)
    print(f"TOP {n} PRODUCTS BY REVENUE")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("product_name")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_amount", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .head(n)
    )
    print(group.to_string())


def payment_breakdown(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("PAYMENT METHOD BREAKDOWN")
    print("=" * 60)
    counts = df["payment_method"].value_counts()
    for method, count in counts.items():
        bar = "█" * (count // max(1, len(df) // 20))
        print(f"  {method:<20} {count:>4}  {bar}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyse sales CSV data")
    parser.add_argument(
        "--input", type=str, default="./data/",
        help="Path to a CSV file or directory of CSVs (default: ./data/)"
    )
    args = parser.parse_args()

    df = load_data(args.input)
    df = preprocess(df)

    summary_stats(df)
    revenue_by_category(df)
    revenue_by_city(df)
    revenue_by_channel(df)
    monthly_trend(df)
    top_products(df)
    payment_breakdown(df)

    print("\n✓ Analysis complete.")


if __name__ == "__main__":
    main()
