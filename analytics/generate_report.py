import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()


def generate_pdf_report():

    logger.info("Generating executive PDF report")

    os.makedirs("reports", exist_ok=True)

    engine = get_engine()
    df = pd.read_sql("SELECT * FROM sales_cleaned", engine)

    # ==============================
    # KPI Calculations
    # ==============================

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders

    df["order_datetime"] = pd.to_datetime(df["order_datetime"])
    df["date"] = df["order_datetime"].dt.date
    df["month"] = df["order_datetime"].dt.to_period("M").astype(str)

    monthly = (
        df.groupby("month")["revenue"]
        .sum()
        .reset_index()
    )

    monthly["growth_%"] = monthly["revenue"].pct_change() * 100

    # ==============================
    # Create Revenue Chart
    # ==============================

    plt.figure()
    daily = df.groupby("date")["revenue"].sum()
    daily.plot()
    plt.title("Daily Revenue Trend")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.tight_layout()

    chart_path = "reports/revenue_chart.png"
    plt.savefig(chart_path)
    plt.close()

    # ==============================
    # PDF Setup
    # ==============================

    pdf_path = "reports/executive_report.pdf"
    doc = SimpleDocTemplate(pdf_path)
    elements = []

    styles = getSampleStyleSheet()

    # IMPORTANT: Place DejaVuSans.ttf in project root
    pdfmetrics.registerFont(TTFont("DejaVuSans", "assets/fonts/DejaVuSans.ttf"))

    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontName="DejaVuSans",
        fontSize=18,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=20
    )

    normal_style = ParagraphStyle(
        name="NormalStyle",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=11
    )

    # ==============================
    # Title
    # ==============================

    elements.append(Paragraph("Coffee Shop Executive Report", title_style))
    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y')}",
            normal_style
        )
    )
    elements.append(Spacer(1, 20))

    # ==============================
    # KPI Table
    # ==============================

    kpi_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"₹ {total_revenue:,.2f}"],
        ["Total Profit", f"₹ {total_profit:,.2f}"],
        ["Total Orders", f"{total_orders:,}"],
        ["Average Order Value", f"₹ {avg_order_value:,.2f}"]
    ]

    table = Table(kpi_data, colWidths=[220, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.lightgrey])
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # ==============================
    # Monthly Growth Table
    # ==============================

    elements.append(Paragraph("Monthly Revenue Growth (%)", title_style))
    elements.append(Spacer(1, 10))

    growth_data = [["Month", "Revenue", "Growth %"]]

    for _, row in monthly.iterrows():
        growth_data.append([
            row["month"],
            f"₹ {row['revenue']:,.2f}",
            f"{row['growth_%']:.2f}" if pd.notna(row["growth_%"]) else "-"
        ])

    growth_table = Table(growth_data, colWidths=[150, 150, 100])
    growth_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(growth_table)
    elements.append(Spacer(1, 30))

    # ==============================
    # Revenue Chart
    # ==============================

    elements.append(Paragraph("Revenue Trend Analysis", title_style))
    elements.append(Spacer(1, 10))

    img = Image(chart_path, width=6*inch, height=3*inch)
    elements.append(img)

    # ==============================
    # Build PDF
    # ==============================

    doc.build(elements)

    logger.info("Executive report saved to reports/executive_report.pdf")
