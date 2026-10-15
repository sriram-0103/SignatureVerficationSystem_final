from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

from datetime import datetime
import os


def generate_pdf(
    output_path,
    customer_name,
    account_number,
    decision,
    confidence,
    similarity,
    reference_features,
    test_features
):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "<b><font size=18>"
            "Signature Verification Report"
            "</font></b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    story.append(
        Paragraph(
            f"<b>Customer :</b> {customer_name}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Account Number :</b> {account_number}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Date :</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    story.append(
        Paragraph(
            f"<b>Decision :</b> {decision}",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Confidence :</b> {confidence:.2f} %",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Similarity :</b> {similarity:.2f} %",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "<b>AI Model :</b> Random Forest",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 0.3 * inch))

    data = [
        [
            "Feature",
            "Reference",
            "Test"
        ]
    ]

    for feature in reference_features:

        data.append([

            feature,

            round(reference_features[feature], 2),

            round(test_features[feature], 2)

        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ])

    )

    story.append(table)

    story.append(Spacer(1, 0.3 * inch))

    story.append(

        Paragraph(

            "<b>Conclusion</b>",

            styles["Heading2"]

        )

    )

    if decision == "Authentic":

        text = (
            "The submitted signature matches the "
            "stored reference template."
        )

    elif decision == "Forgery":

        text = (
            "The submitted signature does not match "
            "the stored reference template."
        )

    else:

        text = (
            "The verification requires manual review."
        )

    story.append(

        Paragraph(

            text,

            styles["Normal"]

        )

    )

    doc.build(story)

    return output_path