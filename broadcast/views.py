import pytz, ast
from datetime import datetime
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client
from django.http import FileResponse
from django.shortcuts import render
from django.template.loader import get_template
from weasyprint import HTML

from .models import Employee, Documents
from .serializers import AnnouncementSerializer
from twilio.base.exceptions import TwilioRestException
from django.core.mail import send_mail
from django.core.mail.message import BadHeaderError
from django.views.generic.base import View
from django.views.generic import ListView


class SendAnnouncementView(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, format=None):
        data = self.build_form_data(request)

        serializer = AnnouncementSerializer(data=data)
        if serializer.is_valid():
            receipients = serializer.validated_data.get('receipients', None)
            receipients = ast.literal_eval(receipients)
            message = serializer.validated_data.get('message', None)
            subject = serializer.validated_data.get('subject', None)
            mode = serializer.validated_data.get('mode', None)
            if mode == 'email':
                self.custom_send_email(receipients, subject, message)
            elif mode in ['sms', 'whatsapp']:
                self.send_sms(receipients, message, mode)

            # Save the message to your database
            serializer.save()

            return Response(
                {'status': 'Message(s) sent successfully'},
                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def build_form_data(self, request):
        data = request.data.dict()
        user_created = request.user
        data.update(
            user_created=user_created.pk,
            broadcast_dt=datetime.now(tz=pytz.timezone('Africa/Gaborone')))

        group = data.get('group', None)
        mode = data.get('mode', None)
        employees = Employee.objects.all()
        # TO DO: Filter employees based on group selected
        if mode in ['sms', 'whatsapp']:
            contacts = employees.values_list('contact_details', flat=True)
            contacts = list(set(contacts))
            data.update(receipients=f'{contacts}')
        elif mode == 'email':
            emails = employees.values_list('user__email', flat=True)
            emails = list(set(emails))
            data.update(receipients=f'{emails}')
        return data

    def send_sms(self, receipients=[], message='', mode='sms'):
        for receipient in receipients:
            # Send the message using Twilio
            to_number = '+267' + receipient
            to_number = 'whatsapp:' + to_number if mode == 'whatsapp' else to_number
            from_ = 'whatsapp:+14345108936' if mode == 'whatsapp' else '+14345108936'
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            try:
                client.messages.create(
                    body=message,
                    from_=from_,
                    to=to_number)
            except TwilioRestException:
                continue

    def custom_send_email(self, receipients=[], subject='', message=''):
        try:
            send_mail(
                subject,
                message,
                'admin@bhp.org.bw',
                receipients,
                fail_silently=False)
        except BadHeaderError:
            pass
            # handle error

 
class Announcements(View):
    def get(self, request, *args, **kwargs):
        return render(request, "confirmation_letter.html")


class GenerateDocument(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, document_type):
        # Document data (e.g., content, user details)
        # Fetch data based on document type and user information

        # Render the HTML template with data
        context = {
            'document_data': self.get_employee_data(request),
        }
        html_template = '/templates/confirmation_letter.html'
        # html_template = get_template('confirmation_letter.html')
        response = render(request, html_template, context)
        html_string = response.content.decode('utf-8')

        # Generate a PDF from the HTML
        pdf = HTML(html_template).write_pdf()

        # Send the PDF as a response
        response = FileResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document_type}.pdf"'
        return response

    def get_employee_data(self, request):
        return {'name': 'Ame Diphoko'}



class DocumentItemList(ListView):
    model = Documents
    template_name = 'generate_doc.html'
    context_object_name = 'items'
