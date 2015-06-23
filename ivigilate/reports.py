from datetime import datetime
from django.db.models import Count
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from ivigilate.models import AuthUser, EventOccurrence


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.setFont("Helvetica", 8)
        self.drawCentredString(self._pagesize[0] / 2, 5 * mm,
                             "Page %d of %d" % (self._pageNumber, page_count))


class Report:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header1 = Paragraph('iVigilate', styles['Heading4'])
        header2 = Paragraph('www.ivigilate.com', styles['Heading4'])
        w, h = header1.wrap(doc.width, doc.topMargin)
        header1.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        w, h = header2.wrap(doc.width, doc.topMargin)
        header2.drawOn(canvas, doc.width - (2*doc.leftMargin), doc.height + doc.topMargin - h)

        canvas.line(doc.leftMargin, doc.height + doc.topMargin - h, doc.leftMargin + w, doc.height + doc.topMargin - h)
        canvas.line(doc.leftMargin, doc.topMargin - h, doc.leftMargin + w, doc.topMargin - h)

        # Footer
        # footer = Paragraph('www.ivigilate.com', styles['Heading5'])
        # w, h = footer.wrap(doc.width, doc.bottomMargin)
        # footer.drawOn(canvas, doc.leftMargin, doc.bottomMargin - h)

        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def _graphout(doc, category_names, data):
        drawing = Drawing(doc.width, 150)
        graph = Pie()
        graph.x = doc.width / 2 - 50
        graph.y = 0
        graph.height = 100
        graph.width = 100
        graph.labels = category_names
        graph.data = data
        graph.slices[0].fillColor = colors.darkcyan
        graph.slices[1].fillColor = colors.blueviolet
        graph.slices[2].fillColor = colors.blue
        graph.slices[3].fillColor = colors.cyan
        graph.slices[4].fillColor = colors.aquamarine
        graph.slices[5].fillColor = colors.cadetblue
        graph.slices[6].fillColor = colors.lightcoral


        drawing.add(graph)
        return drawing

    # https://www.reportlab.com/docs/reportlab-userguide.pdf
    # https://www.reportlab.com/docs/reportlab-graphics-reference.pdf
    def print_event_occurrences(self, account, from_date, to_date):
        MAX_COLUMNS = 4
        MAX_ROWS = 34

        buffer = self.buffer

        doc = SimpleDocTemplate(buffer,
                                rightMargin=cm,
                                leftMargin=cm,
                                topMargin=2*cm,
                                bottomMargin=cm,
                                pagesize=self.pagesize)

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

        # Our container for 'Flowable' objects
        elements = []
        elements.append(Paragraph('Event Occurrence\'s Report', styles['Heading1']))
        if account is not None:
            sub_title = '{0} - from \'{1}\' to \'{2}\''.format(account.name,
                                                               datetime.strftime(from_date, '%Y-%m-%d %H:%M'),
                                                               datetime.strftime(to_date, '%Y-%m-%d %H:%M'))
            elements.append(Paragraph(sub_title, styles['Heading2']))
            elements.append(Spacer(5*mm, 5*mm))

            # Here's where the PDF meaningful data starts.
            eos = EventOccurrence.objects.filter(beacon__account_id=account.id,occurred_at__gte=from_date,occurred_at__lte=to_date)\
                .values('event__name', 'beacon__name')\
                .annotate(num_occurrences=Count('sighting'))

            if eos is not None and len(eos) > 0:
                different_events = []
                different_beacons = []
                handy_dict_event_first = {}
                handy_dict_beacon_first = {}
                column_offset = 0
                for eo in eos:
                    if eo['event__name'] not in different_events:
                        different_events.append(eo['event__name'])
                    if eo['beacon__name'] not in different_beacons:
                        different_beacons.append(eo['beacon__name'])
                    handy_dict_event_first[(eo['event__name'], eo['beacon__name'])] = eo['num_occurrences']
                    handy_dict_beacon_first[(eo['beacon__name'], eo['event__name'])] = eo['num_occurrences']

                if len(different_events) <= len(different_beacons):
                    rows = different_beacons
                    columns = different_events
                    dict_to_use = handy_dict_beacon_first
                    table_fixed_header = 'Beacon \ Event'
                else:
                    rows = different_events
                    columns = different_beacons
                    dict_to_use = handy_dict_event_first
                    table_fixed_header = 'Event \ Beacon'

                while len(columns) - column_offset > 0:
                    row_offset = 0
                    while len(rows) - row_offset > 0:
                        table_data = []
                        table_data.append([table_fixed_header] + sorted(columns[column_offset : column_offset + MAX_COLUMNS]))

                        for row in rows[row_offset : row_offset + MAX_ROWS]:
                            row_items = []
                            row_items.append(row)
                            for column in columns[column_offset : column_offset + MAX_COLUMNS]:
                                row_items.append(dict_to_use.get((row, column), 0))
                            table_data.append(row_items)

                        # Create the table
                        event_occurrence_table = Table(table_data, colWidths=[doc.width / 5.0] * 5)
                        event_occurrence_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                                                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                                                                    ('BACKGROUND', (1, 1), (-1, -1), colors.white),
                                                                    ('ALIGNMENT', (1, 0), (-1, -1), 'CENTER')]))

                        elements.append(event_occurrence_table)
                        row_offset += MAX_ROWS
                        if len(rows) - row_offset > 0:
                            elements.append(PageBreakIfNotEmpty())

                    column_offset += MAX_COLUMNS
                    if len(columns) - column_offset > 0:
                        elements.append(PageBreakIfNotEmpty())

                # elements.append(PageBreakIfNotEmpty())

                # Add pie chart
                # pie_chart = self._graphout(doc, ['AAA','BBB','CCC'], [5,15,1])
                # elements.append(pie_chart)
            else:
                elements.append(Paragraph('Zero items returned', styles['centered']))
        else:
            elements.append(Paragraph('Current user doesn\'t belong to an account', styles['centered']))

        doc.build(elements, onFirstPage=self._header, onLaterPages=self._header, canvasmaker=NumberedCanvas)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf