from django.db.models import Model,CharField,TextField,DateTimeField,ForeignKey,CASCADE
from django.conf import settings
import json

# Create your models here.
class ResearchSession(Model):
    user=ForeignKey(settings.AUTH_USER_MODEL,on_delete=CASCADE)
    title=CharField(max_length=150)
    created_at=DateTimeField(auto_now_add=True)

class Query(Model):
    session=ForeignKey(ResearchSession,on_delete=CASCADE,related_name='queries')
    question=TextField()
    answer=TextField()
    sources=TextField()
    created_at=DateTimeField(auto_now_add=True)

    def get_sources(self):
        try:
            return json.loads(self.sources)
        except:
            return []
