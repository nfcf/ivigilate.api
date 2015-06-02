from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from ivigilate.serializers import *
from rest_framework import permissions, viewsets, status, mixins
from ivigilate import utils
from ivigilate.reports import Report
from io import BytesIO
import json, logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def print_users(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Report.pdf"'

    buffer = BytesIO()

    report = Report(buffer, 'A4')
    pdf = report.print_users()

    response.write(pdf)
    return response
