# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import connection
from nani.test_utils.context_managers import LanguageOverride
from nani.test_utils.data import DOUBLE_NORMAL
from nani.test_utils.testcase import NaniTestCase
from testproject.app.models import Normal


class FilterTests(NaniTestCase):
    fixtures = ['double_normal.json']
    
    def test_simple_filter(self):
        qs = Normal.objects.language('en').filter(shared_field__contains='2')
        self.assertEqual(qs.count(), 1)
        obj = qs[0]
        self.assertEqual(obj.shared_field, DOUBLE_NORMAL[2]['shared_field'])
        self.assertEqual(obj.translated_field, DOUBLE_NORMAL[2]['translated_field_en'])
        qs = Normal.objects.language('ja').filter(shared_field__contains='1')
        self.assertEqual(qs.count(), 1)
        obj = qs[0]
        self.assertEqual(obj.shared_field, DOUBLE_NORMAL[1]['shared_field'])
        self.assertEqual(obj.translated_field, DOUBLE_NORMAL[1]['translated_field_ja'])
        
    def test_translated_filter(self):
        qs = Normal.objects.filter(translated_field__contains='English')
        self.assertEqual(qs.count(), 2)
        obj1, obj2 = qs
        self.assertEqual(obj1.shared_field, DOUBLE_NORMAL[1]['shared_field'])
        self.assertEqual(obj1.translated_field, DOUBLE_NORMAL[1]['translated_field_en'])
        self.assertEqual(obj2.shared_field, DOUBLE_NORMAL[2]['shared_field'])
        self.assertEqual(obj2.translated_field, DOUBLE_NORMAL[2]['translated_field_en'])


class IterTests(NaniTestCase):
    fixtures = ['double_normal.json']
    
    def test_simple_iter(self):
        with LanguageOverride('en'):
            with self.assertNumQueries(1):
                index = 0
                for obj in Normal.objects.language():
                    index += 1
                    self.assertEqual(obj.shared_field, DOUBLE_NORMAL[index]['shared_field'])
                    self.assertEqual(obj.translated_field, DOUBLE_NORMAL[index]['translated_field_en'])
        with LanguageOverride('ja'):
            with self.assertNumQueries(1):
                index = 0
                for obj in Normal.objects.language():
                    index += 1
                    self.assertEqual(obj.shared_field, DOUBLE_NORMAL[index]['shared_field'])
                    self.assertEqual(obj.translated_field, DOUBLE_NORMAL[index]['translated_field_ja'])

class UpdateTests(NaniTestCase):
    fixtures = ['double_normal.json']
    
    def test_update_shared(self):
        NEW_SHARED = 'new shared'
        n1 = Normal.objects.language('en').get(pk=1)
        n2 = Normal.objects.language('en').get(pk=2)
        ja1 = Normal.objects.language('ja').get(pk=1)
        ja2 = Normal.objects.language('ja').get(pk=2)
        with self.assertNumQueries(2):
            Normal.objects.language('en').update(shared_field=NEW_SHARED)
        new1 = Normal.objects.language('en').get(pk=1)
        new2 = Normal.objects.language('en').get(pk=2)
        self.assertEqual(new1.shared_field, NEW_SHARED)
        self.assertEqual(new1.translated_field, n1.translated_field)
        self.assertEqual(new2.shared_field, NEW_SHARED)
        self.assertEqual(new2.translated_field, n2.translated_field)
        # check it didn't touch japanese
        newja1 = Normal.objects.language('ja').get(pk=1)
        newja2 = Normal.objects.language('ja').get(pk=2)
        self.assertEqual(newja1.shared_field, ja1.shared_field)
        self.assertEqual(newja2.shared_field, ja2.shared_field)
        self.assertEqual(newja1.translated_field, ja1.translated_field)
        self.assertEqual(newja2.translated_field, ja2.translated_field)
        
    def test_update_translated(self):
        NEW_TRANSLATED = 'new translated'
        n1 = Normal.objects.language('en').get(pk=1)
        n2 = Normal.objects.language('en').get(pk=2)
        ja1 = Normal.objects.language('ja').get(pk=1)
        ja2 = Normal.objects.language('ja').get(pk=2)
        with self.assertNumQueries(1):
            Normal.objects.language('en').update(translated_field=NEW_TRANSLATED)
        new1 = Normal.objects.language('en').get(pk=1)
        new2 = Normal.objects.language('en').get(pk=2)
        self.assertEqual(new1.shared_field, n1.shared_field)
        self.assertEqual(new2.shared_field, n2.shared_field)
        self.assertEqual(new1.translated_field, NEW_TRANSLATED)
        self.assertEqual(new2.translated_field, NEW_TRANSLATED)
        # check it didn't touch japanese
        newja1 = Normal.objects.language('ja').get(pk=1)
        newja2 = Normal.objects.language('ja').get(pk=2)
        self.assertEqual(newja1.shared_field, ja1.shared_field)
        self.assertEqual(newja2.shared_field, ja2.shared_field)
        self.assertEqual(newja1.translated_field, ja1.translated_field)
        self.assertEqual(newja2.translated_field, ja2.translated_field)