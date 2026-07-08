# Vietnam Local Zone — Sales Data Pipeline

Generate synthetic Vietnamese sales data, analyse it, and transform it into clean, analysis-ready files.

---

## Project structure

```
vietnam-local-zone/
├── data_generator/
│   ├── generate_sales.py       # produces 100-record CSV files
│   └── requirements.txt        # Python dependencies
├── analysis/
│   ├── analyze_sales.py        # descriptive statistics on CSV files (v1)
│   └── analyze_sales_v2.py     # advanced analysis on Parquet files (v2)
├── transformation/
│   └── transform_sales.py      # cleaning & feature engineering → Parquet
├── data/                       # raw generated CSV files
└── cleaned/                    # transformed Parquet files
```

---

## Quick start (local macOS / Linux)

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r data_generator/requirements.txt

# 3. Generate 100-record sample file
python data_generator/generate_sales.py
# → data/sales_001.csv

# 4. Generate multiple files (e.g. 5 × 100 records)
python data_generator/generate_sales.py --files 5 --output data/sales.csv
# → data/sales_001.csv … data/sales_005.csv

# 5. Run analysis on raw CSV
python analysis/analyze_sales.py --input data/

# 6. Run transformation
python transformation/transform_sales.py --input data/
# → cleaned/sales_clean.parquet

# 7. Run advanced analysis on cleaned Parquet
python analysis/analyze_sales_v2.py --input cleaned/
```

---

## Setup on Amazon Linux 2023

Follow these steps on a fresh AL2023 EC2 instance or container.

### 1 — Connect to the instance

```bash
ssh -i your-key.pem ec2-user@<PUBLIC_IP>
```

### 2 — Update the system

```bash
sudo dnf update -y
```

### 3 — Install system dependencies

AL2023 ships with Python 3.9+. Install Python, pip, and the build tools needed to compile pandas/numpy:

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    gcc-c++ \
    make \
    blas \
    blas-devel \
    lapack \
    lapack-devel \
    zlib-devel
```

**Why these packages?**
- `python3`, `python3-pip` — Python runtime and package manager
- `python3-devel`, `gcc`, `gcc-c++`, `make` — C/C++ compilers for building native extensions
- `blas`, `lapack` — Linear algebra libraries required by numpy
- `zlib-devel` — Compression library required by pyarrow

Verify installation:

```bash
python3 --version   # Python 3.9.x or higher
pip3 --version
gcc --version
```

### 4 — Clone or upload the project

**Option A — git clone**

```bash
sudo dnf install -y git
git clone https://github.com/<your-org>/vietnam-local-zone.git
cd vietnam-local-zone
```

**Option B — scp from your local machine**

```bash
scp -i your-key.pem -r ./vietnam-local-zone ec2-user@<PUBLIC_IP>:~/
```

### 5 — Create a virtual environment

```bash
cd ~/vietnam-local-zone
python3 -m venv .venv
source .venv/bin/activate
```

### 6 — Install Python dependencies

Upgrade pip first, then install all packages from `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r data_generator/requirements.txt
```

This installs:

| Package | Version | Used by |
|---|---|---|
| `pandas` | 2.2.2 | All scripts — data loading, filtering, grouping |
| `numpy` | 1.26.4 | pandas dependency — numeric operations |
| `pyarrow` | 14.0.1 | `transform_sales.py`, `analyze_sales_v2.py` — Parquet I/O |

**If you hit a build error** (common on minimal AL2023 images), install pre-built wheels instead:

```bash
pip install --only-binary :all: pandas==2.2.2 numpy==1.26.4 pyarrow==14.0.1
```

**Verify the install:**

```bash
python3 -c "import pandas, numpy, pyarrow; print('All packages OK')"
```

### 7 — Generate sample data

```bash
# Single file — 100 records
python data_generator/generate_sales.py --output data/sales_001.csv

# Multiple files
python data_generator/generate_sales.py --files 5 --output data/sales.csv
```

### 8 — Run analysis on raw CSV

```bash
python analysis/analyze_sales.py --input data/
```

### 9 — Run transformation

```bash
python transformation/transform_sales.py --input data/
```

Output is written to `cleaned/` automatically:
- Directory input → `cleaned/sales_clean.parquet`
- Single file input → `cleaned/<filename>.parquet` (e.g. `cleaned/sales_001.parquet`)

To use a different output folder:

```bash
python transformation/transform_sales.py --input data/ --output-dir processed/
```

### 10 — Run advanced analysis on Parquet

```bash
python analysis/analyze_sales_v2.py --input cleaned/
```

### 11 — (Optional) Run as a cron job

Generate fresh data every day at 08:00 AM:

```bash
crontab -e
```

Add this line:

```cron
0 8 * * * /home/ec2-user/vietnam-local-zone/.venv/bin/python \
  /home/ec2-user/vietnam-local-zone/data_generator/generate_sales.py \
  --output /home/ec2-user/vietnam-local-zone/data/sales_$(date +\%Y\%m\%d).csv \
  >> /home/ec2-user/vietnam-local-zone/data/cron.log 2>&1
```

---

## Script reference

### generate_sales.py

| Argument | Default | Description |
|---|---|---|
| `--records` | `100` | Rows per file |
| `--output` | `../data/sales_001.csv` | Output file path |
| `--files` | `1` | Number of files to generate |

Dependencies: stdlib only — no external packages required.

### analyze_sales.py

| Argument | Default | Description |
|---|---|---|
| `--input` | `./data/` | CSV file or directory |

Dependencies: `pandas`, `numpy`

### analyze_sales_v2.py

| Argument | Default | Description |
|---|---|---|
| `--input` | `./cleaned/` | Parquet file or directory |

Dependencies: `pandas`, `numpy`, `pyarrow`

### transform_sales.py

| Argument | Default | Description |
|---|---|---|
| `--input` | `./data/` | Raw CSV file or directory |
| `--output-dir` | `./cleaned/` | Folder for output Parquet files |

Output filename is derived from the input automatically:
- Directory input → `cleaned/sales_clean.parquet`
- Single file input → `cleaned/<same-stem>.parquet`

Dependencies: `pandas`, `numpy`, `pyarrow`

---

## Output columns — cleaned Parquet file

| Column | Type | Notes |
|---|---|---|
| `order_id` | string | UUID-based unique ID |
| `sale_date` | date | YYYY-MM-DD |
| `month` | string | e.g. `2025-03` |
| `quarter` | string | Q1 – Q4 |
| `day_of_week` | string | Monday … Sunday |
| `product_name` | string | Vietnamese product names |
| `category` | string | Electronics, Clothing, … |
| `unit_price` | int | VND |
| `quantity` | int | 1 – 5 |
| `discount_pct` | int | 0, 5, 10, 15, or 20 |
| `discount_amount` | int | VND discounted off subtotal |
| `total_amount` | int | VND after discount |
| `revenue_tier` | category | Low / Medium / High |
| `is_discounted` | bool | True if discount_pct > 0 |
| `city` | string | Major Vietnamese cities |
| `sales_channel` | string | Online / In-Store / … |
| `payment_method` | string | Cash / Card / … |
| `status` | string | Completed / Pending (cancelled dropped) |
| `sales_rep_id` | string | REP001 – REP020 |
