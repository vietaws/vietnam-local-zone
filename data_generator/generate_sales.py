"""
generate_sales.py
-----------------
Generates synthetic Vietnamese sales sample data.
Produces one CSV file with 100 records per run.

Usage:
    python generate_sales.py
    python generate_sales.py --records 100 --output ../data/sales_001.csv
"""

import argparse
import csv
import os
import random
import uuid
from datetime import datetime, timedelta

# ── Reference data ────────────────────────────────────────────────────────────

PRODUCT_CATALOG = [
    {"name": "Laptop Dell XPS 15",       "category": "Electronics",  "base_price": 32_000_000},
    {"name": "iPhone 15 Pro",            "category": "Electronics",  "base_price": 28_000_000},
    {"name": "Samsung Galaxy S24",       "category": "Electronics",  "base_price": 22_000_000},
    {"name": "Tai nghe Sony WH-1000XM5", "category": "Electronics",  "base_price":  8_500_000},
    {"name": "Áo thun nam Uniqlo",       "category": "Clothing",     "base_price":    450_000},
    {"name": "Váy nữ form A",            "category": "Clothing",     "base_price":    680_000},
    {"name": "Giày Nike Air Max",        "category": "Footwear",     "base_price":  3_200_000},
    {"name": "Giày Adidas Ultraboost",   "category": "Footwear",     "base_price":  3_800_000},
    {"name": "Tủ lạnh LG 300L",         "category": "Appliances",   "base_price": 12_000_000},
    {"name": "Máy giặt Samsung 9kg",     "category": "Appliances",   "base_price": 10_500_000},
    {"name": "Bàn làm việc gỗ",         "category": "Furniture",    "base_price":  2_800_000},
    {"name": "Ghế văn phòng ergonomic",  "category": "Furniture",    "base_price":  4_500_000},
    {"name": "Sách lập trình Python",    "category": "Books",        "base_price":    250_000},
    {"name": "Sách kinh doanh khởi nghiệp","category": "Books",      "base_price":    180_000},
    {"name": "Mỹ phẩm Innisfree",        "category": "Beauty",       "base_price":    320_000},
]

CITIES = [
    "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ",
    "Hải Phòng", "Biên Hòa", "Nha Trang", "Huế",
    "Vũng Tàu", "Quy Nhơn",
]

SALES_CHANNELS = ["Online", "In-Store", "Mobile App", "Reseller"]
PAYMENT_METHODS = ["Cash", "Credit Card", "Bank Transfer", "E-Wallet", "COD"]
STATUSES = ["Completed", "Completed", "Completed", "Pending", "Cancelled"]  # weighted


# ── Generator ─────────────────────────────────────────────────────────────────

def random_date(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between start and end."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def generate_records(n: int = 10000) -> list[dict]:
    """Generate n synthetic sales records."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    records = []
    for _ in range(n):
        product = random.choice(PRODUCT_CATALOG)

        # Add ±20 % price variation to simulate discounts / promotions
        unit_price = int(product["base_price"] * random.uniform(0.80, 1.20))
        quantity = random.randint(1, 5)
        discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20])  # % discount
        subtotal = unit_price * quantity
        discount_amount = int(subtotal * discount_pct / 100)
        total_amount = subtotal - discount_amount

        sale_date = random_date(start_date, end_date)

        records.append({
            "order_id":        str(uuid.uuid4())[:12].upper(),
            "sale_date":       sale_date.strftime("%Y-%m-%d"),
            "sale_time":       sale_date.strftime("%H:%M:%S"),
            "product_name":    product["name"],
            "category":        product["category"],
            "unit_price":      unit_price,
            "quantity":        quantity,
            "discount_pct":    discount_pct,
            "discount_amount": discount_amount,
            "total_amount":    total_amount,
            "city":            random.choice(CITIES),
            "sales_channel":   random.choice(SALES_CHANNELS),
            "payment_method":  random.choice(PAYMENT_METHODS),
            "status":          random.choice(STATUSES),
            "sales_rep_id":    f"REP{random.randint(1, 20):03d}",
        })

    return records


def write_csv(records: list[dict], filepath: str) -> None:
    """Write records to a CSV file."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    fieldnames = list(records[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"✓ Wrote {len(records)} records → {filepath}")


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic sales data")
    parser.add_argument(
        "--records", type=int, default=100,
        help="Number of records to generate (default: 100)"
    )
    parser.add_argument(
        "--output", type=str, default="../data/sales_001.csv",
        help="Output CSV file path (default: ../data/sales_001.csv)"
    )
    parser.add_argument(
        "--files", type=int, default=1,
        help="Number of files to generate (default: 1)"
    )
    args = parser.parse_args()

    if args.files == 1:
        records = generate_records(args.records)
        write_csv(records, args.output)
    else:
        # Generate multiple files: sales_001.csv, sales_002.csv, ...
        base, ext = os.path.splitext(args.output)
        for i in range(1, args.files + 1):
            path = f"{base}_{i:03d}{ext}"
            records = generate_records(args.records)
            write_csv(records, path)

    print("Done.")


if __name__ == "__main__":
    main()
