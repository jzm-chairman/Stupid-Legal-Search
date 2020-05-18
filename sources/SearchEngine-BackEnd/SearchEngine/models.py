from django.db import models
from mongoengine import *


class Appear(EmbeddedDocument):
    paper_id = StringField()
    freq = IntField()
    offset = ListField(IntField())


class InvertedIndex(Document):
    term = StringField(max_length=20)
    appear = EmbeddedDocumentListField(Appear)
    meta = {'collection': 'InvertedIndex'}
