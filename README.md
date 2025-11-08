# LSE Scraper

The goal of this solution is to support **financial analysts, traders, and portfolio managers** who need accurate and timely stock price information from the **London Stock Exchange (LSE)**.  

This project automates the retrieval of the latest stock values for a specified list of stocks (provided in CSV format) and processes them for downstream analysis, reporting, or integration with other tools.

---

## Business Context

Financial professionals often need near real-time stock prices to make informed decisions. Manually visiting the LSE website and copying stock data is time-consuming, error-prone, and inefficient, especially when tracking multiple stocks over time.  

This project addresses these challenges by providing:  

- **Automation**: Scheduled and event-driven data collection using Cron and Watchdog adapters.  
- **Reliability**: Programmatic access to stock prices directly from LSE, ensuring accurate and up-to-date data.  
- **Flexibility**: Multiple adapters (API, CLI, Cron, Watchdog) to match different usage scenarios.  
- **Integration-ready outputs**: Structured CSV files for easy consumption by reporting tools, dashboards, or further processing pipelines.  

**Assumptions:**

- Users provide a CSV file listing stocks symbols they want to track. We need 2 columns: `company name` and `stock code` 
- The system has internet access to fetch data from the LSE website.  
- Only the latest stock price and timestamp are required.
- Users may want to deploy either locally for testing or in a containerized environment for production automation.  

---

## Project Structure

```
/app/core – Core logic and shared modules
/app/utils – Utility modules
/app/api – API adapter
/app/cli – CLI adapter
/app/cron – Cron adapter
/app/watchdog – Watchdog adapter
/app/run_adapters.py – Script to run any adapter or all concurrently
/data – Input/output directories for CLI, Cron, and Watchdog (configurable)
/tests - Tests
/logs – Log files (configurable)
.env – Environment variables for Docker Containers
```


---

## Environment Variables

Create a `.env` file in the root directory:

```env
# --- Common configuration ---
APP_ROOT=/app
LOG_DIR=/logs
LOG_LEVEL=INFO
DATA_DIR=/data

# --- API service ---
API_PORT=8000

# --- CLI service ---
CLI_INPUT=${DATA_DIR}/cli/stocks.csv
CLI_OUTPUT=${DATA_DIR}/cli/stocks_output.csv

# --- CRON service ---
CRON_INPUT=${DATA_DIR}/cron/stocks.csv
CRON_OUTPUT=${DATA_DIR}/cron/stocks_output.csv
CRON_SCHEDULE=*/10 * * * *   # Every 10 minutes

# --- WATCHDOG service ---
WATCHDOG_INPUT_DIR=${DATA_DIR}/watchdog/input
WATCHDOG_OUTPUT_DIR=${DATA_DIR}/watchdog/output
```

## Running with Docker (Recommended)

### 1. Install Docker

Ensure Docker and Docker Compose are installed. Instructions: [Get Docker](https://docs.docker.com/get-started/get-docker/)

### 2. Build Base Docker Image

Install Playwright dependencies once in a base image:

``` bash
docker build -f Dockerfile.base -t app-base:latest . 
```
### 3. Start all services

```bash
docker compose up --build
```

### 4. Run individual services
``` bash
docker compose up api
docker compose up cli
docker compose up cron
docker compose up watchdog
```

## Running with Python

### 1. create and activate visual environment 

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r app/api/requirements.txt
pip install -r app/cli/requirements.txt
pip install -r app/cron/requirements.txt
pip install -r app/watchdog/requirements.txt
pip install playwright
playwright install chromium
```

### 3. Run individual service or all of them concurrently
```commandline
python run_adapters.py api

python run_adapters.py cli -i path/to/input.csv -o path/to/output.csv

python run_adapters.py cron -i path/to/input.csv -o path/to/output.csv --cron "*/10 * * * *"

python run_adapters.py watchdog -i path/to/input_dir -o path/to/output_dir

python run_adapters.py all \
  --cli-input path/to/input.csv \
  --cli-output path/to/output.csv \
  --cron-input path/to/input.csv \
  --cron-output path/to/output.csv \
  --cron-expr "*/10 * * * *" \
  --watchdog-input-dir path/to/input_dir \
  --watchdog-output-dir path/to/output_dir
```

### 4. Troubleshooting

Sometimes Chromium will fail to run due to missing system libraries:
* On Linux, install missing packages using your package manager. Common ones include:

```bash
sudo apt-get update
sudo apt-get install -y \
    libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libgbm1 libxcb1 libxkbcommon0 libasound2 libatspi2.0-0 libexpat1
```

