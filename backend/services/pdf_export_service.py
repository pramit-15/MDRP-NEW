import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.utils.logger import get_logger

logger = get_logger("pdf_export_service")

class PDFExportService:
    def generate_prediction_pdf(self, prediction_data: dict) -> io.BytesIO:
        """
        Generates a professional clinical PDF report for a prediction record.
        Returns a BytesIO stream containing the PDF binary.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom typography styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1e3a8a"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155")
        )
        body_bold = ParagraphStyle(
            'ReportBodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748b")
        )

        elements = []

        # ── Header ──────────────────────────────────────────────────────────
        header_data = [
            [
                Paragraph("<b>MDRP Clinical Intelligence Platform</b><br/><font size=8 color='#64748b'>Multi-Disease Risk Prediction & Guidance</font>", body_style),
                Paragraph(f"<b>Report ID:</b> {prediction_data.get('id', 'N/A')[:8]}...<br/><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[340, 200])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

        # Title
        elements.append(Paragraph("Patient Health Risk Assessment Report", title_style))
        elements.append(Paragraph("Synthesized Risk Scoring from Stacking Ensemble Machine Learning & Clinical Practice Guidelines (ACC/AHA 2019, ADA 2024, KDIGO 2022)", subtitle_style))

        # ── Overall Composite Risk Summary ──────────────────────────────────
        heart = float(prediction_data.get("heart_risk", prediction_data.get("heart", 0)))
        diabetes = float(prediction_data.get("diabetes_risk", prediction_data.get("diabetes", 0)))
        kidney = float(prediction_data.get("kidney_risk", prediction_data.get("kidney", 0)))
        composite = round(heart * 0.4 + diabetes * 0.35 + kidney * 0.25, 1)

        level_color = "#10b981" if composite < 25 else "#f59e0b" if composite < 50 else "#ef4444"
        level_text = "LOW RISK" if composite < 25 else "MODERATE RISK" if composite < 50 else "HIGH RISK"

        summary_box_data = [
            [
                Paragraph(f"<b>Overall Composite Health Risk</b><br/><font size=24 color='{level_color}'><b>{composite:.1f}%</b></font> <font size=10 color='{level_color}'>({level_text})</font>", body_style),
                Paragraph(f"<b>Cardiovascular Risk:</b> {heart:.1f}%<br/><b>Type 2 Diabetes Risk:</b> {diabetes:.1f}%<br/><b>Chronic Kidney Risk:</b> {kidney:.1f}%", body_style)
            ]
        ]
        summary_table = Table(summary_box_data, colWidths=[270, 270])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10))

        # ── Detailed Risk Breakdown Table ──────────────────────────────────
        elements.append(Paragraph("1. Tri-Disease Risk & Scoring Synthesis", section_heading))
        scores_detail = prediction_data.get("scores_detail", {})
        
        disease_data = [
            ["Condition / Target", "ML Ensemble Prob.", "Clinical Guideline", "Blended Risk (40/60)"],
            [
                "Cardiovascular Disease (Heart)",
                f"{scores_detail.get('heart', {}).get('ml', heart):.1f}%",
                f"{scores_detail.get('heart', {}).get('clinical', 0):.0f}/100",
                f"{heart:.1f}%"
            ],
            [
                "Type 2 Diabetes Mellitus",
                f"{scores_detail.get('diabetes', {}).get('ml', diabetes):.1f}%",
                f"{scores_detail.get('diabetes', {}).get('clinical', 0):.0f}/100",
                f"{diabetes:.1f}%"
            ],
            [
                "Chronic Kidney Disease (CKD)",
                f"{scores_detail.get('kidney', {}).get('ml', kidney):.1f}%",
                f"{scores_detail.get('kidney', {}).get('clinical', 0):.0f}/100",
                f"{kidney:.1f}%"
            ],
        ]
        disease_table = Table(disease_data, colWidths=[180, 120, 120, 120])
        disease_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(disease_table)
        elements.append(Spacer(1, 10))

        # ── AI Health Improvement Suggestions ──────────────────────────────
        ai_sugg = prediction_data.get("ai_suggestions", {})
        if ai_sugg and isinstance(ai_sugg, dict):
            elements.append(Paragraph("2. AI Health Insights & Personalized Action Plan", section_heading))
            if ai_sugg.get("summary"):
                elements.append(Paragraph(f"<b>Assessment Summary:</b> {ai_sugg.get('summary')}", body_style))
                elements.append(Spacer(1, 4))
            
            if ai_sugg.get("top_priority"):
                priority_box = Table(
                    [[Paragraph(f"<b>Top Priority Action:</b> {ai_sugg.get('top_priority')}", body_style)]],
                    colWidths=[540]
                )
                priority_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef3c7")),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#f59e0b")),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(priority_box)
                elements.append(Spacer(1, 6))

            # Actionable items list
            lifestyle = ai_sugg.get("lifestyle_suggestions", [])
            for item in lifestyle:
                elements.append(Paragraph(f"• <b>{item.get('category')}: {item.get('title')}</b> ({item.get('priority')} Priority)", body_bold))
                elements.append(Paragraph(f"  {item.get('advice')}", body_style))
                actions = item.get("action_items", [])
                if actions:
                    for act in actions:
                        elements.append(Paragraph(f"    - {act}", body_style))
                elements.append(Spacer(1, 4))

        elements.append(Spacer(1, 6))

        # ── Laboratory Biomarkers Table ───────────────────────────────────
        inputs = prediction_data.get("inputs_used", {})
        if inputs:
            elements.append(Paragraph("3. Patient Laboratory & Physiological Panel", section_heading))
            biomarker_rows = [["Biomarker / Measure", "Value", "Biomarker / Measure", "Value"]]
            
            items_list = list(inputs.items())
            for i in range(0, len(items_list), 2):
                k1, v1 = items_list[i]
                k2, v2 = items_list[i+1] if i+1 < len(items_list) else ("", "")
                val1_str = f"{v1:.2f}" if isinstance(v1, float) else str(v1)
                val2_str = f"{v2:.2f}" if isinstance(v2, float) else str(v2) if v2 != "" else ""
                biomarker_rows.append([k1.upper(), val1_str, k2.upper() if k2 else "", val2_str])

            biomarker_table = Table(biomarker_rows, colWidths=[170, 100, 170, 100])
            biomarker_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(biomarker_table)

        elements.append(Spacer(1, 14))

        # ── Disclaimer & Signature Block ──────────────────────────────────
        disclaimer_text = (
            "<b>Clinical Disclaimer:</b> This report is generated by the Multi-Disease Risk Prediction (MDRP) "
            "platform combining machine learning models and evidence-based clinical scoring rules. It is provided for "
            "educational and clinical decision-support purposes only and does not replace professional medical judgment, "
            "diagnosis, or treatment. Always consult a licensed healthcare provider before making medical decisions."
        )
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        elements.append(Spacer(1, 16))

        sig_data = [
            [
                Paragraph("<b>Reviewing Clinician:</b> ___________________________", body_style),
                Paragraph("<b>Date / Signature:</b> ___________________________", body_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        elements.append(sig_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer

pdf_export_service = PDFExportService()
