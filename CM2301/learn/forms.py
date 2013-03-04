from django.forms import ModelForm
from learn.models import *
from django.forms import ModelForm, DateInput

class AttachmentForm(ModelForm):
    class Meta:
        model = Attachment

class VideoUploadForm(ModelForm):
    class Meta:
        model = Video
        
class LectureCreateForm(ModelForm):
    class Meta:
        model = Lecture
        exclude = ('id', 'visible')
        widgets = {
            'valid_to': DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yy'}),
            'valid_from': DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yy'}),
        }
        
class RevisionCreateForm(ModelForm):
    class Meta:
        model = Revision
        #fields = ('file',)
        
