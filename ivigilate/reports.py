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
from ivigilate.models import AuthUser


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
        self.drawCentredString(self._pagesize[0] / 2, 2 * mm,
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
        header2 = Paragraph('http://www.ivigilate.com', styles['Heading4'])
        w, h = header1.wrap(doc.width, doc.topMargin)
        header1.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        w, h = header2.wrap(doc.width, doc.topMargin)
        header2.drawOn(canvas, doc.width - (3*doc.leftMargin), doc.height + doc.topMargin - h)

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

    def print_users(self):
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
        elements.append(Paragraph("iVigilate Report", styles["Heading1"]))
        elements.append(Paragraph("http://www.ivigilate.com", styles["Normal"]))

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        users = AuthUser.objects.all()
        elements.append(Paragraph('List of Users', styles['Heading1']))
        for i, user in enumerate(users):
            elements.append(Paragraph(user.get_full_name(), styles['Normal']))

        # Need a place to store our table rows
        table_data = []
        for i, user in enumerate(users):
            # Add a row to the table
            table_data.append([user.get_full_name(), user.email, user.last_login])
        # Create the table
        user_table = Table(table_data, colWidths=[doc.width/3.0]*3)
        user_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(user_table)

        # elements.append(Spacer(5*mm, 5*mm))

        # Add pie chart
        pie_chart = self._graphout(doc, ['AAA','BBB','CCC'], [5,15,1])
        elements.append(pie_chart)

        doc.build(elements, onFirstPage=self._header, onLaterPages=self._header,
                  canvasmaker=NumberedCanvas)


        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf