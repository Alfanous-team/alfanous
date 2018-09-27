from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Visit (models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField( max_length = 15 ) #may be this should be the key
    host = models.CharField( max_length = 255 )
    referer = models.CharField( max_length = 255 )
    request = models.CharField( max_length = 255 )
    query = models.CharField( max_length=255)
    sorted_by = models.CharField( max_length=10)
    recitation = models.CharField( max_length=30)
    translation =  models.CharField( max_length=30)

    def __unicode__(self):
            return u"%d.%s" % (self.id,self.query)

class Aya(models.Model):
    id = models.IntegerField(primary_key=True,db_column='gid')
    sura_id = models.IntegerField(null=True, blank=True)
    aya_id = models.IntegerField(null=True, blank=True)
    standard = models.TextField(blank=True)
    standard_full = models.TextField(blank=True)
    uthmani = models.TextField(blank=True)
    uthmani_min = models.TextField(blank=True)
    chapter = models.TextField(blank=True)
    topic = models.TextField(blank=True)
    subtopic = models.TextField(blank=True)
    subject = models.TextField(blank=True)
    rub_gid = models.IntegerField(null=True, blank=True)
    nisf_gid = models.IntegerField(null=True, blank=True)
    hizb_gid = models.IntegerField(null=True, blank=True)
    juz_gid = models.IntegerField(null=True, blank=True)
    rub_id = models.IntegerField(null=True, blank=True)
    nisf_id = models.IntegerField(null=True, blank=True)
    hizb_id = models.IntegerField(null=True, blank=True)
    juz_id = models.IntegerField(null=True, blank=True)
    page_id = models.IntegerField(null=True, blank=True)
    ruku_id = models.IntegerField(null=True, blank=True)
    manzil_id = models.IntegerField(null=True, blank=True)
    sajda = models.CharField(max_length=10, blank=True)
    sajda_id = models.IntegerField(null=True, blank=True)
    sajda_type = models.CharField(max_length=10, blank=True)
    sura_name = models.CharField(max_length=20, blank=True)
    sura_type = models.CharField(max_length=30, blank=True)
    sura_order = models.IntegerField(null=True, blank=True)
    sura_ayas_nb = models.IntegerField(null=True, blank=True)
    sura_gnames_nb = models.IntegerField(null=True, blank=True)
    sura_words_nb = models.IntegerField(null=True, blank=True)
    sura_letters_nb = models.IntegerField(null=True, blank=True)
    sura_rukus_nb = models.IntegerField(null=True, blank=True)
    aya_gnames_nb = models.IntegerField(null=True, blank=True)
    aya_words_nb = models.IntegerField(null=True, blank=True)
    aya_letters_nb = models.IntegerField(null=True, blank=True)
    page_id_indian = models.IntegerField(null=True, blank=True)
    sura_name_en = models.CharField(max_length=25, blank=True)
    sura_name_romanization = models.CharField(max_length=25, blank=True)
    sura_type_en = models.CharField(max_length=10, blank=True)
    class Meta:
        db_table = 'aya'

class Field(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20, blank=True)
    name_arabic = models.CharField(max_length=20, blank=True)
    table_name = models.CharField(max_length=10, blank=True)
    comment = models.TextField(blank=True)
    type = models.CharField(max_length=20, blank=True)
    format = models.CharField(max_length=20, blank=True)
    is_indexed = models.IntegerField(null=True, blank=True)
    is_stored = models.IntegerField(null=True, blank=True)
    is_spellchecked = models.IntegerField(null=True, blank=True)
    is_scorable = models.IntegerField(null=True, blank=True)
    is_unique = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=30, blank=True)
    source_comment = models.TextField(blank=True)
    revised = models.IntegerField(null=True, blank=True)
    revised_by = models.CharField(max_length=30, blank=True)
    search_name = models.CharField(max_length=20, blank=True)
    analyser = models.CharField(max_length=20, blank=True)
    boost = models.CharField(max_length=20, blank=True)
    phrase = models.CharField(max_length=20, blank=True)
    lock = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'field'

class Stopwords(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=10, unique=True, blank=True)
    nb_in_quran = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'stopwords'

class Synonymes(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=15, unique=True, blank=True)
    synonymes = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = 'synonymes'

class Word(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=20, blank=True)
    word_field = models.CharField(max_length=20, db_column='word_', blank=True) # Field renamed because it ended with '_'.
    uthmani = models.CharField(max_length=20, blank=True)
    lemma = models.CharField(max_length=20, blank=True)
    root = models.CharField(max_length=10, blank=True)
    type = models.CharField(max_length=50, blank=True)
    pattern = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=20, blank=True)
    person = models.CharField(max_length=20, blank=True)
    i3rab = models.CharField(max_length=20, blank=True)
    class Meta:
        db_table = 'word'