import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()


def _styled_table(data, col_widths, header_color="#1F4E79", font_size=10):
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    return table


def _build_charts(df):
    chart_paths = {}

    daily = df.groupby("date", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
    plt.figure(figsize=(10, 4))
    plt.plot(daily["date"], daily["revenue"], label="Revenue", linewidth=2)
    plt.plot(daily["date"], daily["profit"], label="Profit", linewidth=2)
    plt.title("Daily Revenue vs Profit")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_paths["trend"] = "reports/revenue_profit_trend.png"
    plt.savefig(chart_paths["trend"])
    plt.close()

    category_rev = (
        df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    )
    plt.figure(figsize=(8, 4))
    plt.bar(category_rev["category"], category_rev["revenue"], color="#2E75B6")
    plt.title("Revenue by Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    plt.tight_layout()
    chart_paths["category"] = "reports/revenue_by_category.png"
    plt.savefig(chart_paths["category"])
    plt.close()

    payment_mix = df.groupby("payment_type", as_index=False)["revenue"].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(
        payment_mix["revenue"],
        labels=payment_mix["payment_type"],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title("Revenue Mix by Payment Type")
    plt.tight_layout()
    chart_paths["payment"] = "reports/payment_mix.png"
    plt.savefig(chart_paths["payment"])
    plt.close()

    return chart_paths

def generate_pdf_report():
    logger.info("Generating executive PDF report")
    os.makedirs("reports", exist_ok=True)

    os.makedirs("reports", exist_ok=True)

    engine = get_engine()
    df = pd.read_sql("SELECT * FROM sales_cleaned", engine)

    if df.empty:
        logger.warning("No data found in sales_cleaned. Skipping executive report generation.")
        return

    df["order_datetime"] = pd.to_datetime(df["order_datetime"], errors="coerce")
    df = df.dropna(subset=["order_datetime"]).copy()

    df["date"] = df["order_datetime"].dt.date
    df["month"] = df["order_datetime"].dt.to_period("M").astype(str)

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders if total_orders else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    total_qty = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).sum()

    monthly = df.groupby("month", as_index=False)["revenue"].sum()
    monthly["growth_%"] = monthly["revenue"].pct_change() * 100

    monthly["growth_%"] = monthly["revenue"].pct_change() * 100

    top_products = (
        df.groupby("product_name", as_index=False)
        .agg(revenue=("revenue", "sum"), qty=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
        .head(5)
    )

    payment_summary = (
        df.groupby("payment_type", as_index=False)
        .agg(revenue=("revenue", "sum"), transactions=("order_id", "count"))
        .sort_values("revenue", ascending=False)
    )

    chart_paths = _build_charts(df)

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
           spaceAfter=16,
    )
    section_style = ParagraphStyle(
        name="SectionStyle",
        parent=styles["Heading2"],
        fontName="DejaVuSans",
        fontSize=13,
        textColor=colors.HexColor("#2E75B6"),
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        name="NormalStyle",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=10,
    )


    elements.append(Paragraph("Coffee Shop Executive Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y')}", normal_style))
    elements.append(Spacer(1, 16))

    kpi_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"₹ {total_revenue:,.2f}"],
        ["Total Profit", f"₹ {total_profit:,.2f}"],
        ["Profit Margin", f"{profit_margin:.2f}%"],
        ["Total Orders", f"{total_orders:,}"],
        ["Total Quantity Sold", f"{int(total_qty):,}"],
        ["Average Order Value", f"₹ {avg_order_value:,.2f}"],
    ]

    elements.append(Paragraph("Business KPIs", section_style))
    elements.append(_styled_table(kpi_data, [220, 200]))
    elements.append(Spacer(1, 16))

    growth_data = [["Month", "Revenue", "Growth %"]]

    for _, row in monthly.iterrows():
        growth_data.append([
            row["month"],
            f"₹ {row['revenue']:,.2f}",
            f"{row['growth_%']:.2f}" if pd.notna(row["growth_%"]) else "-",
        ])
    elements.append(Paragraph("Monthly Revenue Growth", section_style))
    elements.append(_styled_table(growth_data, [140, 170, 140], header_color="#2E75B6", font_size=9))
    elements.append(Spacer(1, 16))

    product_data = [["Product", "Revenue", "Quantity"]]
    for _, row in top_products.iterrows():
        product_data.append([
            row["product_name"],
            f"₹ {row['revenue']:,.2f}",
            f"{int(row['qty']):,}",
        ])
    elements.append(Paragraph("Top 5 Products", section_style))
    elements.append(_styled_table(product_data, [180, 170, 100], header_color="#3C8D40", font_size=9))
    elements.append(Spacer(1, 16))

    payment_data = [["Payment Type", "Revenue", "Transactions"]]
    for _, row in payment_summary.iterrows():
        payment_data.append([
            row["payment_type"],
            f"₹ {row['revenue']:,.2f}",
            f"{int(row['transactions']):,}",
        ])
    elements.append(Paragraph("Payment Channel Summary", section_style))
    elements.append(_styled_table(payment_data, [160, 170, 120], header_color="#955196", font_size=9))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Trend Analysis", section_style))
    elements.append(Image(chart_paths["trend"], width=6.3 * inch, height=2.7 * inch))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Category & Payment Insights", section_style))
    elements.append(Image(chart_paths["category"], width=6.3 * inch, height=2.7 * inch))
    elements.append(Spacer(1, 10))

    elements.append(Image(chart_paths["payment"], width=4.2 * inch, height=4.0 * inch))

    doc.build(elements)

    logger.info("Executive report saved to reports/executive_report.pdf")
