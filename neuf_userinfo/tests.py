from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status


class IndexViewTest(TestCase):
    def test_index_view(self):
        url = reverse('index')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
