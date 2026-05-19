# AW Client Report Portal

The AW Client Report Portal is a lightweight, full-stack application built for a boutique financial planning firm. It automates the firm's previously manual process of aggregating client financial data and generating production-ready, pixel-perfect **Simple Automated Cashflow System (SACS)** and **Total Client Chart (TCC)** PDF reports.

By strictly separating the structural account setup ("Taxonomy") from quarterly data entry ("Hydration"), the portal turns a full-day reporting chore into a 2-minute frictionless workflow for the administrative team.

---

## Key Features

*   **Progressive Client Setup:** A robust taxonomy builder to define the "skeleton" of a client's wealth. Tag accounts by Owner (Client 1, Client 2, Joint) and Category (Retirement, Non-Retirement, Liability, Trust).
*   **Intelligent Auto-Calculations:** The backend automatically calculates precise ages, aggregates joint salaries, and runs formulas for Private Reserve Targets `(6x Budget + Deductibles)`.
*   **Frictionless Data Hydration:** At the end of the quarter, the portal fetches the client's static skeleton and generates a streamlined form asking *only* for the current balances, pre-filling last quarter's numbers as a visual reference.
*   **Pixel-Perfect PDF Generation:** Uses ReportLab's geometric primitives to dynamically draw and route exact mathematical flowcharts and quadrant-based net-worth diagrams, seamlessly mirroring the firm's premium aesthetic standards.
*   **Glassmorphic UI:** A responsive, modern Vanilla JS single-page application (SPA) requiring zero build steps, keeping the architecture extremely maintainable for a small team.

## Technology Stack

*   **Backend:** Python 3, Flask
*   **Database:** SQLite3 (Serverless, lightweight, portable)
*   **PDF Engine:** ReportLab
*   **Frontend:** Vanilla HTML5, CSS3 (Custom Glassmorphism), Vanilla JavaScript
*   **Architecture:** Decoupled RESTful JSON API

## Project Structure

```text
c:\dev\aw-client-portal\
│
├── app.py                  # Core Flask server and REST API routes
├── database.py             # SQLite schema initialization and data access layer
├── pdf_generator.py        # ReportLab mathematical geometric layout engine
├── reset_db.py             # Utility script to instantly rebuild the local DB schema
├── requirements.txt        # Python dependencies
│
├── static/                 # Frontend SPA Assets (Served statically)
│   ├── index.html          # Progressive UI layout
│   ├── script.js           # API integration and DOM state management
│   └── style.css           # Design system (Variables, Flexbox, Glassmorphism)
│
└── reports/                # Local directory where generated PDFs are temporarily saved
```

## Local Development Setup

To run this portal on your local machine:

1. **Clone the repository and navigate to the directory:**
   ```bash
   cd c:\dev\aw-client-portal
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install Flask reportlab
   ```

4. **Initialize the application:**
   ```bash
   python app.py
   ```
   *Note: On its first run, `app.py` automatically initializes the `database.sqlite` file and builds the required tables using the logic in `database.py`.*

## Deployment (Render & Railway)

This application is structurally prepared for instant deployment on PaaS platforms.

### 1. Render (Recommended)
The repository includes a `render.yaml` file for **Render Blueprints**. 
- Go to Render -> **New Blueprint Instance** and connect this repository. Render will automatically detect the Python environment, install dependencies, and configure Gunicorn.
- **Persistence Note:** By default, Render Web Services have ephemeral storage. To keep your SQLite database from resetting on deploy, attach a **Render Disk** to your web service and set the `RAILWAY_DATABASE_PATH` (or rename it to `DB_PATH`) environment variable to point to the mount path of the disk.

### 2. Railway
The application is also configured for Railway. The SQLite connection engine uses the `RAILWAY_DATABASE_PATH` environment variable natively. Attach a Railway persistent volume and map this environment variable to seamlessly persist the firm's CRM data.

## Resetting the Database
During development, if you need to completely clear all clients and accounts and reset the database schema, simply run the utility script:
```bash
python reset_db.py
```
This will cleanly drop all tables so they can be rebuilt fresh upon the next server restart.
