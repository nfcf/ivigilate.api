from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from ivigilate.serializers import *
from rest_framework import permissions, viewsets, status, mixins
from ivigilate import utils
from rest_framework import permissions, viewsets, status, views
from ivigilate.reports import Report
from io import BytesIO
import json, logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class EventOccurrenceReportView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        account = request.user.account if request.user is not None else None
        now = datetime.now(timezone.utc)
        from_date_default = datetime.strftime(datetime(now.year, now.month, now.day-1, now.hour, now.minute, now.second), '%Y-%m-%dT%H:%M:%S')
        to_date_default = datetime.strftime(datetime(now.year, now.month, now.day, now.hour, now.minute, now.second), '%Y-%m-%dT%H:%M:%S')
        report_type = request.query_params.get('report_type', None)
        from_date = datetime.strptime(request.query_params.get('from_date', from_date_default), '%Y-%m-%dT%H:%M:%S')
        to_date = datetime.strptime(request.query_params.get('to_date', to_date_default), '%Y-%m-%dT%H:%M:%S')

        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        buffer = BytesIO()

        report = Report(buffer, 'A4')
        if report_type == 'EO':
            pdf = report.print_event_occurrences(account, from_date, to_date)

            response.write(pdf)
            return response
        else:
            return Response('Invalid report type...', status=status.HTTP_400_BAD_REQUEST)
