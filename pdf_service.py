"""
FoodGenie Printable PDF Generator using ReportLab
Generates a real, clean multi-section Food Cart & Daily Nutrition PDF from user's saved database cart.
"""

from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from model_user import User
from schema_cart import CartResponse

ROYAL_PURPLE = colors.HexColor("#351078")
LAVENDER_MIST = colors.HexColor("#F2ECFF")
LIGHT_BLUE = colors.HexColor("#ADD8E6")
ELECTRIC_LIME = colors.HexColor("#C6FF00")
TEXT_DARK = colors.HexColor("#230852")
MUTED_SLATE = colors.HexColor("#475569")
SOFT_BORDER = colors.HexColor("#D8C5FF")


def _pdf_safe(text: object) -> str:
    """Normalizes Unicode symbols unsupported in Helvetica (like INR sign) to clean printable text."""
    raw = str(text if text is not None else "")
    return raw.replace("₹", "Rs. ").encode("latin-1", "replace").decode("latin-1")


def generate_food_cart_pdf(user: User, cart: CartResponse) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="FoodGenie - My Food Cart Plan",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "FGTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.white,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "FGSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=colors.HexColor("#E5DAFB"),
    )
    section_style = ParagraphStyle(
        "FGSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=ROYAL_PURPLE,
        spaceBefore=10,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "FGCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=TEXT_DARK,
    )
    note_style = ParagraphStyle(
        "FGNote",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=MUTED_SLATE,
    )

    user_name = _pdf_safe(user.full_name or user.email.split("@")[0].title())
    gen_date = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    story = []

    # 1. Branded Header Banner
    banner_data = [[
        Paragraph("FOODGENIE &mdash; Personal Food Cart &amp; Nutrition Plan", title_style),
        Paragraph(f"<b>Prepared For:</b> {user_name}<br/><b>Email:</b> {_pdf_safe(user.email)}<br/><b>Generated:</b> {gen_date}", subtitle_style),
    ]]
    banner_table = Table(banner_data, colWidths=[108 * mm, 70 * mm])
    banner_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ROYAL_PURPLE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # 2. Daily Nutrition & Budget Summary
    story.append(Paragraph("Daily Nutrition &amp; Estimated Budget Summary", section_style))
    totals = cart.totals
    summary_rows = [
        ["Metric", "Cart Total", "Daily Reference / Budget", "Notes"],
        ["Total Calories", f"{totals.total_calories:.0f} kcal", f"{totals.daily_calorie_target} kcal", f"{totals.calorie_target_percent:.1f}% of target"],
        ["Total Protein", f"{totals.total_protein_g:.1f} g", "ICMR/USDA ref", "Muscle & tissue support"],
        ["Total Carbohydrates", f"{totals.total_carbs_g:.1f} g", "Balanced wholefoods", "Primary energy source"],
        ["Total Fats", f"{totals.total_fat_g:.1f} g", "Healthy lipids", "Nutrient absorption"],
        ["Total Dietary Fiber", f"{totals.total_fiber_g:.1f} g", "30 g/day adult ref", "Digestive & glycemic balance"],
        ["Total Estimated Budget", f"Rs. {totals.total_estimated_cost_inr:.2f}", f"Rs. {totals.daily_budget_inr:.2f} / day", f"{totals.total_items} selected food item(s)"],
    ]
    sum_table = Table(summary_rows, colWidths=[45 * mm, 38 * mm, 45 * mm, 50 * mm])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ROYAL_PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 1), (-1, -2), LAVENDER_MIST),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BLUE),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, SOFT_BORDER),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 10))

    # 3. Selected Food Items Organized by Meal Category
    story.append(Paragraph(f"Selected Foods ({_pdf_safe(cart.title)})", section_style))

    if not cart.items:
        story.append(Paragraph("Your Food Cart currently has no items. Add recommended foods in FoodGenie to populate your plan.", cell_style))
    else:
        item_rows = [[
            "Meal Slot",
            "Food & Key Nutrients",
            "Qty",
            "Calories",
            "Macros (P/C/F)",
            "Est. Price",
        ]]
        for slot, slot_items in cart.grouped_meals.items():
            for it in slot_items:
                micros = ", ".join((it.vitamins_summary[:2] + it.minerals_summary[:2]))
                food_desc = f"<b>{_pdf_safe(it.food_name)}</b>"
                if micros:
                    food_desc += f"<br/><font size='7.5' color='#475569'>{_pdf_safe(micros)}</font>"
                item_rows.append([
                    Paragraph(f"<b>{_pdf_safe(slot)}</b>", cell_style),
                    Paragraph(food_desc, cell_style),
                    Paragraph(_pdf_safe(f"{it.quantity:g} x {it.serving_size}"), cell_style),
                    Paragraph(f"{it.total_calories:.0f} kcal", cell_style),
                    Paragraph(f"{it.total_protein_g:.1f}g / {it.total_carbs_g:.1f}g / {it.total_fat_g:.1f}g", cell_style),
                    Paragraph(f"<b>Rs. {it.total_estimated_cost_inr:.2f}</b>", cell_style),
                ])

        items_table = Table(item_rows, colWidths=[26 * mm, 56 * mm, 28 * mm, 20 * mm, 28 * mm, 20 * mm], repeatRows=1)
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ROYAL_PURPLE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LAVENDER_MIST]),
            ("GRID", (0, 0), (-1, -1), 0.5, SOFT_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(items_table)

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "Disclaimer: Nutritional breakdowns are calculated from ICMR-NIN Indian Food Composition Tables & USDA reference benchmarks, "
        "and retail prices shown are estimated market averages in INR. Consult a registered dietitian or physician for clinical medical nutrition.",
        note_style,
    ))

    doc.build(story)
    return buf.getvalue()

