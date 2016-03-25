import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.response import Response
from ivigilate.serializers import *
from rest_framework import permissions, viewsets, status, views, mixins
from ivigilate import utils
from datetime import datetime
from dateutil.relativedelta import relativedelta
from suds.client import Client
import pytz, json, logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BcloseSightingView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    PARTNER_TOKEN = 'ivigilate_hash_token'

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8') or '{}')

        company_id = data.get('company_id', None)
        event_id = data.get('event_id', None)
        detector_uid = data.get('detector_uid', None)
        beacon_uid = data.get('beacon_uid', None)
        occur_date = data.get('occur_date', None)

        try:
            client = Client('http://ssn.sysvalue.com/ws/ws_ivigilate/wsdl')
            response = client.service.WsNewSighting(partner_token=self.PARTNER_TOKEN,
                                                    sighting_code=int(event_id),
                                                    customer_id=company_id,
                                                    beacon_uid=beacon_uid,
                                                    detector_uid=detector_uid,
                                                    localdate=datetime.strptime(occur_date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d-%H:%M:%S'))
        except Exception as ex:
            logger.exception('Failed while sending message to Bclose:')
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

        return Response('', status=status.HTTP_200_OK)