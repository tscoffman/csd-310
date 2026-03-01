"""
===================================================================================
Title: Module 10.1 Milestone 3: Creating Wilson Financial Reports
Original Author: Wade Eckert, Trenten Coffman
Date Modified: 26 February 2026
Description: This script connects to the MySQL database, runs queries to generate three 
key reports for Wilson Financial, and saves them as PDFs. The reports include:
1. New Clients Added in the Last 6 Months (with a line chart)
2. Assets Under Management (AUM) Snapshot, Totals and Averages
3. High-Transaction Clients (more than 10 transactions in a month)
===================================================================================
"""

from __future__ import annotations 

import os 
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import mysql.connector # MySQL Connector/Python (used to connect and query the MySQL database)
from mysql.connector import errorcode

from dotenv import dotenv_values # python-dotenv (used for DB credentials from .env file)

"""ReportLab (used to generate PDF reports)"""
from reportlab.lib import colors 
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

import matplotlib.pyplot as plt # Matplotlib (used to enhance Report 1)


"""The ReportConfig dataclass centralizes all table and column names used in the report queries.
This makes it easy to update the code if the database schema changes, and it keeps the query strings clean and readable.""" 
@dataclass(frozen=True) # frozen=True makes it immutable.
class ReportConfig:
    
    # Table and column names 
    employees_table: str = "employees"
    clients_table: str = "clients"
    accounts_table: str = "accounts"
    assets_table: str = "assets"
    holdings_table: str = "holdings"
    transactions_table: str = "transactions"

    # Clients
    client_id_col: str = "client_id"
    client_advisor_id_col: str = "advisor_id"
    client_first_name_col: str = "first_name"
    client_last_name_col: str = "last_name"
    client_start_date_col: str = "start_date"
    client_active_flag_col: str = "active_flag"

    # Accounts
    account_id_col: str = "account_id"
    account_client_id_col: str = "client_id"
    account_type_col: str = "account_type"
    account_opened_date_col: str = "opened_date"
    account_active_flag_col: str = "active_flag"

    # Holdings 
    holding_account_id_col: str = "account_id"
    holding_value_usd_col: str = "value_usd"
    holding_value_as_of_date_col: str = "value_as_of_date"

    # Transactions
    txn_account_id_col: str = "account_id"
    txn_date_col: str = "transaction_date"
    txn_id_col: str = "transaction_id"

REPORT_CONFIG = ReportConfig()


"""Define a function to establish a connection to the MySQL database using credentials stored in a .env file."""
def get_db_connection() -> mysql.connector.MySQLConnection:
    
    secrets = dotenv_values(".env")

    missing = [k for k in ("USER", "PASSWORD", "HOST", "DATABASE") if k not in secrets]
    if missing:
        raise RuntimeError(
            "Missing .env keys: " + ", ".join(missing) + ". "
            "Create a .env file with USER, PASSWORD, HOST, DATABASE."
        )

    config = {
        "user": secrets["USER"],
        "password": secrets["PASSWORD"],
        "host": secrets["HOST"],
        "database": secrets["DATABASE"],
        "raise_on_warnings": True,
    }

    try:
        db = mysql.connector.connect(**config)
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise RuntimeError("The supplied username or password are invalid") from err
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            raise RuntimeError("The specified database does not exist") from err
        raise


"""Define a function to run a query and return all rows. This is a simple helper that we can reuse for different queries."""
def fetchall(db: mysql.connector.MySQLConnection, query: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
    cur = db.cursor()
    try:
        cur.execute(query, params or ()) # execute the query with parameters (if any)
        return cur.fetchall()
    finally:
        cur.close()


"""Define a function to run a query and return both column names and rows. This is useful for building tables in the PDF reports with proper headers."""
def fetchall_with_headers(db: mysql.connector.MySQLConnection, query: str, params: Tuple[Any, ...] | None = None) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    cur = db.cursor()
    try:
        cur.execute(query, params or ())
        headers = [d[0] for d in cur.description]
        rows = cur.fetchall()
        return headers, rows
    finally:
        cur.close()


"""Define a function to build a styled table for the PDF reports. This function takes in the data and optional 
column widths, and it applies consistent styling to make the tables look professional and easy to read."""
def _build_table(data: List[List[Any]], col_widths: Sequence[float] | None = None) -> Table:
    table = Table(data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


"""Define a function to format currency values consistently across the reports. This function attempts to convert the input 
to a float and format it as USD, but if it fails (for example, if the value is None or not a number), it will return the 
original value as a string."""
def _format_currency(value: Any) -> str:
    try:
        if value is None:
            return ""
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)


"""Define a function to format integer values with commas for thousands separators. Similar to the currency formatter, it will
attempt to convert the input to an integer and format it, but if it fails, it will return the original value as a string."""
def _format_int(value: Any) -> str:
    try:
        if value is None:
            return ""
        return f"{int(value):,}"
    except Exception:
        return str(value)


"""Define a function to create and save a simple line chart using Matplotlib. This is an enhancement for Report 1 to visually show 
the trend of new clients added over the last 6 months."""
def _save_line_chart(month_labels: List[str], counts: List[int], out_path: Path) -> None:
    plt.figure(figsize=(8.5, 3.2))
    plt.plot(month_labels, counts, marker="o")
    plt.title("New clients added per month (last 6 months)")
    plt.xlabel("Month")
    plt.ylabel("New clients")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


"""Define SQL query functions for each report. These functions take the ReportConfig as an argument and return the SQL query string.
This approach keeps the SQL organized and allows for easy updates if the database schema changes."""
def query_clients_added_last_6_months(cfg: ReportConfig) -> str:
    # Counts clients by start_date over the last 6 months.
    return f"""
        SELECT
            DATE_FORMAT({cfg.client_start_date_col}, '%Y-%m') AS month,
            COUNT(*) AS new_clients
        FROM {cfg.clients_table}
        WHERE {cfg.client_start_date_col} >= (CURRENT_DATE - INTERVAL 6 MONTH)
          AND {cfg.client_active_flag_col} = 1
        GROUP BY DATE_FORMAT({cfg.client_start_date_col}, '%Y-%m')
        ORDER BY month;
    """.strip() # .strip() is just to clean up any leading/trailing whitespace for better readability in the code.


"""The query for average assets uses the holdings table as a snapshot of AUM. It finds the most recent 'value_as_of_date' in the holdings, 
sums the USD value of all holdings at that date, and calculates averages per active client and per active account."""
def query_average_assets(cfg: ReportConfig) -> str:
    # Uses holdings as the AUM snapshot. We take the most recent value_as_of_date in holdings,
    # then sum value_usd at that snapshot.
    return f"""
        WITH latest AS (
            SELECT MAX({cfg.holding_value_as_of_date_col}) AS as_of_date
            FROM {cfg.holdings_table}
        )
        SELECT
            (SELECT COUNT(*) FROM {cfg.clients_table} WHERE {cfg.client_active_flag_col} = 1) AS total_clients,
            (SELECT COUNT(*) FROM {cfg.accounts_table} WHERE {cfg.account_active_flag_col} = 1) AS total_accounts,
            l.as_of_date AS holdings_as_of_date,
            SUM(h.{cfg.holding_value_usd_col}) AS total_assets_usd,
            ROUND(SUM(h.{cfg.holding_value_usd_col}) / NULLIF((SELECT COUNT(*) FROM {cfg.clients_table} WHERE {cfg.client_active_flag_col} = 1), 0), 2) AS avg_assets_per_client_usd,
            ROUND(SUM(h.{cfg.holding_value_usd_col}) / NULLIF((SELECT COUNT(*) FROM {cfg.accounts_table} WHERE {cfg.account_active_flag_col} = 1), 0), 2) AS avg_assets_per_account_usd
        FROM {cfg.holdings_table} h
        JOIN latest l
          ON h.{cfg.holding_value_as_of_date_col} = l.as_of_date
        GROUP BY l.as_of_date;
    """.strip()


"""The query for high-transaction clients identifies any client who has more than 10 transactions in a single month during the last six months.
It joins the transactions, accounts, and clients tables to count transactions per client per month, and then filters for those with counts greater than 10."""
def query_high_transaction_clients(cfg: ReportConfig) -> str:
    return f"""
        WITH monthly AS (
            SELECT
                c.{cfg.client_id_col} AS client_id,
                CONCAT(c.{cfg.client_last_name_col}, ', ', c.{cfg.client_first_name_col}) AS client_name,
                DATE_FORMAT(t.{cfg.txn_date_col}, '%Y-%m') AS month,
                COUNT(*) AS txn_count
            FROM {cfg.transactions_table} t
            JOIN {cfg.accounts_table} a
              ON a.{cfg.account_id_col} = t.{cfg.txn_account_id_col}
            JOIN {cfg.clients_table} c
              ON c.{cfg.client_id_col} = a.{cfg.account_client_id_col}
            WHERE t.{cfg.txn_date_col} >= (CURRENT_DATE - INTERVAL 6 MONTH)
              AND c.{cfg.client_active_flag_col} = 1
              AND a.{cfg.account_active_flag_col} = 1
            GROUP BY c.{cfg.client_id_col}, client_name, DATE_FORMAT(t.{cfg.txn_date_col}, '%Y-%m')
        )
        SELECT
            client_id,
            client_name,
            month,
            txn_count
        FROM monthly
        WHERE txn_count > 10
        ORDER BY txn_count DESC, month DESC, client_name ASC;
    """.strip()


"""Define functions to build each of the three reports. Each function takes the database connection, output PDF path, and ReportConfig as arguments.
The functions run the appropriate query, format the results into tables and charts, and generate a PDF report using ReportLab."""
def build_report_1_clients_added(db: mysql.connector.MySQLConnection, out_pdf: Path, workdir: Path, cfg: ReportConfig) -> None:
    # Report 1: New Clients Added in the Last 6 Months (with a line chart)
    styles = getSampleStyleSheet()
    story: List[Any] = []

    title = "Report 1: New Clients Added (Last 6 Months)"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    headers, rows = fetchall_with_headers(db, query_clients_added_last_6_months(cfg))

    # Table data for the PDF table, starting with headers. We will also prepare data for the line chart.
    table_data: List[List[Any]] = [headers]
    month_labels: List[str] = []
    counts: List[int] = []

    for month, new_clients in rows:
        month_labels.append(str(month))
        counts.append(int(new_clients))
        table_data.append([str(month), _format_int(new_clients)])

    story.append(Paragraph("Monthly count of newly added clients, grouped by calendar month.", styles["BodyText"]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(_build_table(table_data, col_widths=[2.2 * inch, 2.0 * inch]))

    # Chart (only if we have data to show)
    if rows:
        story.append(Spacer(1, 0.25 * inch))
        chart_path = workdir / "clients_added_last_6_months.png"
        _save_line_chart(month_labels, counts, chart_path)
        story.append(Paragraph("Trend chart (visual aid)", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Image(str(chart_path), width=6.5 * inch, height=2.4 * inch))

    doc = SimpleDocTemplate(str(out_pdf), pagesize=LETTER, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    doc.build(story)


"""Report 2: Assets Under Management (AUM) Snapshot, Totals and Averages. This report estimates AUM using the holdings table as a snapshot.
It pulls the most recent holdings 'value_as_of_date', sums the USD value across all holdings at that date, then calculates averages per active 
client and per active account."""
def build_report_2_average_assets(db: mysql.connector.MySQLConnection, out_pdf: Path, cfg: ReportConfig) -> None:
    styles = getSampleStyleSheet()
    story: List[Any] = []

    title = "Report 2: Assets Under Management (AUM) Snapshot, Totals and Averages"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    headers, rows = fetchall_with_headers(db, query_average_assets(cfg))

    # If holdings are empty, fall back to zeros so the PDF still renders cleanly.
    if not rows or rows[0][0] is None:
        rows = [(0, 0, None, 0.0, 0.0, 0.0)]

    (
        total_clients,
        total_accounts,
        holdings_as_of_date,
        total_assets_usd,
        avg_assets_per_client_usd,
        avg_assets_per_account_usd,
    ) = rows[0]

    data = [
        ["Metric", "Value"],
        ["Holdings snapshot date (value_as_of_date)", str(holdings_as_of_date) if holdings_as_of_date else "N/A"],
        ["Total active clients", _format_int(total_clients)],
        ["Total active accounts", _format_int(total_accounts)],
        ["Total assets (USD)", _format_currency(total_assets_usd)],
        ["Average assets per client (USD)", _format_currency(avg_assets_per_client_usd)],
        ["Average assets per account (USD)", _format_currency(avg_assets_per_account_usd)],
    ]

    story.append(Paragraph(
        "This report estimates assets under management (AUM) using the holdings table as a snapshot. "
        "It pulls the most recent holdings 'value_as_of_date', sums the USD value across all holdings "
        "at that date, then calculates averages per active client and per active account. "
        "The result gives Wilson Financial a quick, defensible baseline for client profitability analysis, "
        "capacity planning, and evaluating whether the current billing approach should be adjusted (for example, "
        "to better match fees to portfolio size).",
        styles["BodyText"],
    ))
    story.append(Spacer(1, 0.15 * inch))

    story.append(_build_table(data, col_widths=[3.2 * inch, 3.0 * inch]))

    doc = SimpleDocTemplate(str(out_pdf), pagesize=LETTER, leftMargin=0.75 * inch, rightMargin=0.75 * inch)
    doc.build(story)


"""Report 3: High-Transaction Clients (More Than 10 Transactions in a Month). This report identifies clients who place a heavy operational load 
on the firm by finding any client who exceeds 10 transactions in a single month during the last six months."""
def build_report_3_high_txn_clients(db: mysql.connector.MySQLConnection, out_pdf: Path, cfg: ReportConfig) -> None:
    styles = getSampleStyleSheet()
    story: List[Any] = []

    title = "Report 3: High-Transaction Clients (More Than 10 Transactions in a Month)"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    headers, rows = fetchall_with_headers(db, query_high_transaction_clients(cfg))

    story.append(Paragraph(
        "This report identifies clients who place a heavy operational load on the firm by finding any client who exceeds "
        "10 transactions in a single month during the last six months. It is useful for understanding where staff time "
        "is being consumed (trade processing, client calls, paperwork, follow-ups), and it can support future decisions "
        "about service tiers, workload balancing, and whether a revised billing structure should account for transaction volume.",
        styles["BodyText"],
    ))
    story.append(Spacer(1, 0.15 * inch))

    table_data: List[List[Any]] = [headers]

    if rows:
        for client_id, client_name, month, txn_count in rows:
            table_data.append([str(client_id), str(client_name), str(month), _format_int(txn_count)])
    else:
        table_data.append(["(none)", "", "", ""])  # nice empty state

    story.append(_build_table(table_data, col_widths=[0.9 * inch, 2.8 * inch, 1.3 * inch, 1.0 * inch]))

    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    doc.build(story)


"""Define the main function."""
def main() -> None:
    # Create an output directory for the reports if it doesn't exist
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Create a working directory for any intermediate files (like charts) that we need to generate for the reports.
    workdir = out_dir / "_assets"
    workdir.mkdir(parents=True, exist_ok=True)

    # Connect to the database and generate the reports.
    db = None
    try:
        db = get_db_connection()
        print(
            "\n  Connected to MySQL on host {} with database {}".format(
                db.server_host if hasattr(db, "server_host") else "(host)",
                db.database if hasattr(db, "database") else "(database)",
            )
        )

        # Build PDFs
        pdf1 = out_dir / "clients_added_last_6_months.pdf"
        pdf2 = out_dir / "average_assets_summary.pdf"
        pdf3 = out_dir / "high_transaction_clients.pdf"

        build_report_1_clients_added(db, pdf1, workdir, REPORT_CONFIG)
        build_report_2_average_assets(db, pdf2, REPORT_CONFIG)
        build_report_3_high_txn_clients(db, pdf3, REPORT_CONFIG)

        print("\n  Reports generated:")
        print(f"   - {pdf1}")
        print(f"   - {pdf2}")
        print(f"   - {pdf3}")

    except mysql.connector.Error as err:
        # keep a nice error message similar to mysql_test.py
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("  The supplied username or password are invalid")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("  The specified database does not exist")
        else:
            print(err)
        raise
    finally:
        if db is not None and db.is_connected():
            db.close()

# Run the main function when this script is executed.
if __name__ == "__main__":
    main()
