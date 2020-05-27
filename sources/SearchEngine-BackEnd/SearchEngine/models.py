import pymongo


# class Paper():
#     pid = IntField(primary_key=True)
#     path = StringField()
#     ajlb = StringField()
#     spcx = StringField()
#     wszl = StringField()
#     xzqh_p = StringField()
#     jand = StringField()
#
#
# class AppearanceD(Document):
#     aid = IntField(primary_key=True)
#     pid = IntField()
#     freq = IntField()
#     score = FloatField()
#     # offset = ListField(IntField())
#
#
# class Appearance(EmbeddedDocument):
#     pid = IntField()
#     freq = IntField()
#     score = FloatField()
#     # offset = ListField(IntField())
#
#
# class InvertedIndex(Document):
#     term = StringField()
#     appear_list = EmbeddedDocumentListField(Appearance)
#     meta = {'collection': 'InvertedIndex'}
