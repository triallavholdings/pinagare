from django.urls import path
from .views import SendAnnouncementView, Announcements, GenerateDocument, DocumentItemList

urlpatterns = [
    path('send-announcement/', SendAnnouncementView.as_view(), name='send_announcement'),
    path('generate-doc/<str:document_type>', GenerateDocument.as_view(), name='generate_doc'),
    path('documents', DocumentItemList.as_view(), name='documents'),
    path('',Announcements.as_view(),name="announcements")
]