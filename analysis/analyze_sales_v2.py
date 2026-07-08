"""
analyze_sales_v2.py
-------------------
Runs advanced analysis on cleaned Parquet sales data.

Enhancements over v1:
  - Reads Parquet files (already preprocessed by transform_sales.py)
  - Revenue tier analysis
  - Discount impact analysis
  - Day-of-week and quarter trends
  - Sales rep performance

Usage:
    python analysis/analyze_sales_v2.py --input ./cleaned/sales_001.parquet
    python analysis/analyze_sales_v2.py --input ./cleaned/  # all Parquet files
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
    """Load one Parquet file or all Parquet files in a directory."""
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "*.parquet"))
        if not files:
            raise FileNotFoundError(f"No Parquet files found in {path}")
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        print(f"Loaded {len(files)} file(s) → {len(df)} total records")
    else:
        df = pd.read_parquet(path)
        print(f"Loaded {len(df)} records from {path}")
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


def revenue_tier_analysis(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("REVENUE TIER BREAKDOWN")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("revenue_tier", observed=True)
        .agg(
            orders=("order_id", "count"),
            total_revenue=("total_amount", "sum"),
            avg_order_value=("total_amount", "mean"),
        )
        .sort_values("total_revenue", ascending=False)
    )
    print(group.to_string())
    print()
    for tier in group.index:
        pct = group.loc[tier, "orders"] / group["orders"].sum() * 100
        print(f"  {tier:<8} tier represents {pct:>5.1f}% of orders")


def discount_impact(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("DISCOUNT IMPACT ANALYSIS")
    print("=" * 60)
    completed = df[df["status"] == "Completed"]
    
    discounted = completed[completed["is_discounted"]]
    non_discounted = completed[~completed["is_discounted"]]
    
    print(f"  Discounted orders       : {len(discounted):,} ({len(discounted)/len(completed)*100:.1f}%)")
    print(f"  Non-discounted orders   : {len(non_discounted):,} ({len(non_discounted)/len(completed)*100:.1f}%)")
    print()
    print(f"  Avg order value (discounted)     : {discounted['total_amount'].mean():>20,.0f} VND")
    print(f"  Avg order value (non-discounted) : {non_discounted['total_amount'].mean():>20,.0f} VND")
    print()
    print(f"  Total revenue (discounted)       : {discounted['total_amount'].sum():>20,.0f} VND")
    print(f"  Total revenue (non-discounted)   : {non_discounted['total_amount'].sum():>20,.0f} VND")
    
    # Discount percentage breakdown
    print("\n  Breakdown by discount level:")
    discount_groups = (
        completed[completed["is_discounted"]]
        .groupby("discount_pct")
        .agg(orders=("order_id", "count"), revenue=("total_amount", "sum"))
        .sort_index()
    )
    print(discount_groups.to_string())


def day_of_week_trend(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("REVENUE BY DAY OF WEEK")
    print("=" * 60)
    
    # Order weekdays correctly
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_completed = df[df["status"] == "Completed"].copy()
    df_completed["day_of_week"] = pd.Categorical(df_completed["day_of_week"], categories=weekday_order, ordered=True)
    
    group = (
        df_completed
        .groupby("day_of_week", observed=False)
        .agg(orders=("order_id", "count"), revenue=("total_amount", "sum"))
        .sort_index()
    )
    print(group.to_string())


def quarterly_trend(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("QUARTERLY REVENUE TREND")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("quarter")
        .agg(orders=("order_id", "count"), revenue=("total_amount", "sum"))
        .sort_index()
    )
    print(group.to_string())


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


def sales_rep_performance(df: pd.DataFrame, n: int = 10) -> None:
    print("\n" + "=" * 60)
    print(f"TOP {n} SALES REPS BY REVENUE")
    print("=" * 60)
    group = (
        df[df["status"] == "Completed"]
        .groupby("sales_rep_id")
        .agg(
            orders=("order_id", "count"),
            revenue=("total_amount", "sum"),
            avg_order_value=("total_amount", "mean"),
        )
        .sort_values("revenue", ascending=False)
        .head(n)
    )
    print(group.to_string())


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyse sales Parquet data (v2)")
    parser.add_argument(
        "--input", type=str, default="./cleaned/",
        help="Path to a Parquet file or directory of Parquet files (default: ./cleaned/)"
    )
    args = parser.parse_args()

    df = load_data(args.input)

    summary_stats(df)
    revenue_tier_analysis(df)
    discount_impact(df)
    day_of_week_trend(df)
    quarterly_trend(df)
    revenue_by_category(df)
    revenue_by_city(df)
    revenue_by_channel(df)
    top_products(df)
    sales_rep_performance(df)

    print("\n✓ Analysis complete.")


if __name__ == "__main__":
    main()
