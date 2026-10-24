from io import BytesIO
from typing import Dict, Any
from datetime import datetime
import re
import html

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image

from core.chart_exporter import (
    generate_price_technical_chart_img,
    generate_radar_chart_img,
    generate_correlation_heatmap_img,
    generate_portfolio_growth_chart_img,
    generate_sector_bar_chart_img
)


def safe_text(val: Any) -> str:
    if val is None:
        return ""
    return html.escape(str(val), quote=False)


def format_reportlab_text(text: str) -> str:
    if not text:
        return ""
    escaped = html.escape(str(text), quote=False)
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escaped)


def generate_pdf_bytes(session_data: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    COLOR_TEXT = colors.HexColor("#0F172A")
    COLOR_MUTED = colors.HexColor("#64748B")
    COLOR_HEADER_BG = colors.HexColor("#F1F5F9")
    COLOR_BORDER = colors.HexColor("#E2E8F0")
    COLOR_ACCENT = colors.HexColor("#0284C7")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_TEXT,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=COLOR_MUTED,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_ACCENT,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT,
        leftIndent=12,
        spaceAfter=4
    )

    story = []

    ticker = session_data.get("ticker", "N/A")
    company = session_data.get("company_name", ticker)
    curr = session_data.get("currency_symbol", "₹")
    dhs = session_data.get("dhs", {})
    technicals = session_data.get("technicals", {})
    fundamentals = session_data.get("fundamentals", {})
    risk = session_data.get("risk_metrics", {})
    insights = session_data.get("insights", [])

    # 1. Header Banner
    story.append(Paragraph("THE EXECUTIVE TERMINAL", ParagraphStyle("HeaderSub", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=COLOR_ACCENT)))
    story.append(Paragraph(f"{safe_text(ticker)} — {safe_text(company)}", title_style))

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dhs_score = dhs.get("dhs_score", 100.0)
    dhs_status = dhs.get("status", "High Quality")
    story.append(Paragraph(f"Generated: {timestamp_str}  |  Data Health Score: <b>{dhs_score}% ({safe_text(dhs_status)})</b>", subtitle_style))

    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER, spaceBefore=0, spaceAfter=8))

    # 2. Executive Takeaways
    story.append(Paragraph("EXECUTIVE TAKEAWAYS & DECISION SUPPORT", section_heading))
    for item in insights:
        formatted_item = format_reportlab_text(item)
        story.append(Paragraph(f"• {formatted_item}", bullet_style))
    story.append(Spacer(1, 8))

    # 3. Technical & Fundamental Charts Grid
    story.append(Paragraph("TECHNICAL & FUNDAMENTAL ANALYSIS CHARTS", section_heading))

    price_img_buf = generate_price_technical_chart_img(session_data.get("ohlcv", []), ticker=ticker)
    radar_img_buf = generate_radar_chart_img(session_data.get("radar_scores", {}), ticker=ticker)

    chart_cells = []
    if price_img_buf:
        chart_cells.append(Image(price_img_buf, width=320, height=180))
    else:
        chart_cells.append(Paragraph("Price Chart Unavailable", body_style))

    if radar_img_buf:
        chart_cells.append(Image(radar_img_buf, width=210, height=180))
    else:
        chart_cells.append(Paragraph("Radar Chart Unavailable", body_style))

    chart_table = Table([chart_cells], colWidths=[330, 210])
    chart_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 2)
    ]))
    story.append(chart_table)
    story.append(Spacer(1, 8))

    # 4. Technical & Fundamental Overview Grid
    story.append(Paragraph("TECHNICAL & FUNDAMENTAL METRICS", section_heading))
    curr_safe = safe_text(curr)
    tf_data = [
        [
            Paragraph(f"<b>Current Price:</b> {curr_safe}{technicals.get('current_price', 0.0):,}", body_style),
            Paragraph(f"<b>EMA 20 / 50 / 200:</b> {technicals.get('ema_20')} / {technicals.get('ema_50')} / {technicals.get('ema_200')}", body_style)
        ],
        [
            Paragraph(f"<b>RSI (14-Day):</b> {technicals.get('rsi_14')} ({safe_text(technicals.get('rsi_status', 'Neutral'))})", body_style),
            Paragraph(f"<b>EMA Alignment:</b> {safe_text(technicals.get('ema_cross'))}", body_style)
        ],
        [
            Paragraph(f"<b>P/E Ratio:</b> {fundamentals.get('pe_ratio')}", body_style),
            Paragraph(f"<b>Debt-to-Equity:</b> {fundamentals.get('debt_to_equity')}", body_style)
        ],
        [
            Paragraph(f"<b>Operating Margin:</b> {round((fundamentals.get('operating_margin') or 0.0)*100, 1)}%", body_style),
            Paragraph(f"<b>Return on Equity (ROE):</b> {round((fundamentals.get('roe') or 0.0)*100, 1)}%", body_style)
        ]
    ]

    tf_table = Table(tf_data, colWidths=[270, 270])
    tf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXT),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(tf_table)
    story.append(Spacer(1, 8))

    # 5. Portfolio Growth & Correlation Visualizations
    bench_symbol = session_data.get("benchmark_symbol", "^NSEI")
    corr_img_buf = generate_correlation_heatmap_img(risk.get("correlation_matrix"))
    growth_img_buf = generate_portfolio_growth_chart_img(bench_name=bench_symbol)

    if corr_img_buf or growth_img_buf:
        story.append(Paragraph("PORTFOLIO RISK & CORRELATION VISUALIZATIONS", section_heading))
        port_chart_cells = []
        if growth_img_buf:
            port_chart_cells.append(Image(growth_img_buf, width=270, height=160))
        else:
            port_chart_cells.append(Paragraph("Growth Chart N/A", body_style))

        if corr_img_buf:
            port_chart_cells.append(Image(corr_img_buf, width=260, height=160))
        else:
            port_chart_cells.append(Paragraph("Correlation N/A", body_style))

        port_chart_table = Table([port_chart_cells], colWidths=[270, 270])
        port_chart_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 2)
        ]))
        story.append(port_chart_table)
        story.append(Spacer(1, 8))

    # 6. Peer Valuation Matrix
    peer_matrix = session_data.get("peer_matrix", [])
    if peer_matrix:
        story.append(Paragraph("PEER COMPARATIVE VALUATION MATRIX", section_heading))
        peer_table_data = [["Ticker", "P/E", "P/S", "EV/EBITDA", "Op. Margin", "ROE"]]
        for row in peer_matrix:
            peer_table_data.append([
                safe_text(row.get("Ticker", "")),
                safe_text(row.get("P/E", "")),
                safe_text(row.get("P/S", "")),
                safe_text(row.get("EV/EBITDA", "")),
                safe_text(row.get("Operating Margin", "")),
                safe_text(row.get("ROE", ""))
            ])

        peer_table = Table(peer_table_data, colWidths=[140, 80, 80, 80, 80, 80])
        peer_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_TEXT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (1, 0), (-1, -1), "CENTER")
        ]))
        story.append(peer_table)

    doc.build(story)
    return buffer.getvalue()