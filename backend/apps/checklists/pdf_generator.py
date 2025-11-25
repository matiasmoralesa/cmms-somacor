"""PDF Generator for Checklist Responses"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChecklistPDFGenerator:
    """Generate PDF reports for completed checklists matching original format"""
    
    def __init__(self, checklist_response):
        self.checklist = checklist_response
        self.template = checklist_response.template
        self.asset = checklist_response.asset
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#444444'),
            spaceAfter=3
        ))
    
    def generate(self):
        """Generate PDF and return BytesIO buffer"""
        try:
            doc = SimpleDocTemplate(
                self.buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Build PDF content
            story = []
            
            # Header
            story.extend(self._build_header())
            story.append(Spacer(1, 0.3*inch))
            
            # Asset and checklist info
            story.extend(self._build_info_section())
            story.append(Spacer(1, 0.2*inch))
            
            # Checklist items table
            story.extend(self._build_checklist_table())
            story.append(Spacer(1, 0.2*inch))
            
            # Score and signature section
            story.extend(self._build_footer())
            
            # Build PDF
            doc.build(story)
            self.buffer.seek(0)
            
            return self.buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF for checklist {self.checklist.id}: {e}")
            raise
    
    def _build_header(self):
        """Build PDF header with title and code"""
        elements = []
        
        # Title
        title = Paragraph(
            f"<b>{self.template.name}</b>",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Code
        code = Paragraph(
            f"Código: {self.template.code}",
            self.styles['CustomBody']
        )
        elements.append(code)
        
        return elements
    
    def _build_info_section(self):
        """Build information section with asset and completion details"""
        elements = []
        
        # Create info table
        info_data = [
            ['Activo:', self.asset.name, 'Código:', self.asset.asset_code],
            ['Tipo:', self.asset.get_vehicle_type_display(), 'Patente:', self.asset.license_plate or 'N/A'],
            ['Operador:', self.checklist.operator_name, 'Turno:', self.checklist.shift or 'N/A'],
            ['Fecha:', self.checklist.completed_at.strftime('%d/%m/%Y %H:%M'), 
             'Horómetro/Km:', str(self.checklist.odometer_reading) if self.checklist.odometer_reading else 'N/A'],
        ]
        
        info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(info_table)
        
        return elements
    
    def _build_checklist_table(self):
        """Build checklist items table"""
        elements = []
        
        # Table header
        heading = Paragraph("<b>Items de Inspección</b>", self.styles['CustomHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.1*inch))
        
        # Group responses by section
        sections = {}
        response_dict = {r['item_order']: r for r in self.checklist.responses}
        
        for item in self.template.items:
            section = item.get('section', 'General')
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
        
        # Build table data
        table_data = [['#', 'Pregunta', 'Respuesta', 'Observaciones']]
        
        for section_name, items in sections.items():
            # Section header row
            table_data.append([
                {'text': section_name, 'colspan': 4, 'background': colors.HexColor('#d0d0d0')}
            ])
            
            # Items in section
            for item in items:
                order = item['order']
                question = item['question']
                response_data = response_dict.get(order, {})
                response = response_data.get('response', 'N/A')
                notes = response_data.get('notes', '')
                
                # Format response
                if response == 'yes':
                    response_text = '✓ Sí'
                elif response == 'no':
                    response_text = '✗ No'
                elif response == 'na':
                    response_text = 'N/A'
                else:
                    response_text = response
                
                table_data.append([
                    str(order),
                    question,
                    response_text,
                    notes[:50] + '...' if len(notes) > 50 else notes
                ])
        
        # Create table
        checklist_table = Table(
            table_data,
            colWidths=[0.5*inch, 3*inch, 1*inch, 2.5*inch]
        )
        
        # Apply table style
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        # Add section header styles
        row_idx = 1
        for section_name in sections.keys():
            style_commands.append(
                ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#d0d0d0'))
            )
            style_commands.append(
                ('SPAN', (0, row_idx), (-1, row_idx))
            )
            style_commands.append(
                ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold')
            )
            row_idx += len(sections[section_name]) + 1
        
        checklist_table.setStyle(TableStyle(style_commands))
        elements.append(checklist_table)
        
        return elements
    
    def _build_footer(self):
        """Build footer with score and signature"""
        elements = []
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Score section
        score_data = [
            ['Puntaje Obtenido:', f"{self.checklist.score}%"],
            ['Puntaje Mínimo:', f"{self.template.passing_score}%"],
            ['Estado:', 'APROBADO ✓' if self.checklist.passed else 'NO APROBADO ✗']
        ]
        
        score_table = Table(score_data, colWidths=[2*inch, 2*inch])
        
        score_bg_color = colors.HexColor('#d4edda') if self.checklist.passed else colors.HexColor('#f8d7da')
        
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('BACKGROUND', (1, 2), (1, 2), score_bg_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(score_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Signature section
        signature_data = [
            ['Completado por:', self.checklist.completed_by.get_full_name()],
            ['Firma:', '']
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(signature_table)
        
        # Footer text
        elements.append(Spacer(1, 0.2*inch))
        footer_text = Paragraph(
            f"<i>Documento generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>",
            self.styles['CustomBody']
        )
        elements.append(footer_text)
        
        return elements
