import ujson

from sanicms.tests import APITestCase
from server import app

class TestCase(APITestCase):
    _app = app
    _blueprint = 'visit'

    def setUp(self):
        super(TestCase, self).setUp()
        self._mock.get('/cities/1',
                       payload={'id': 1, 'name': 'shanghai'})
        self._mock.get('/roles/1',
                       payload={'id': 1, 'name': 'shanghai'})

    def test_create_user(self):
        data = {
            'name': 'test',
            'age': 2,
            'city_id': 1,
            'role_id': 1,
        }
        res = self.client.create_user(data=data)
        body = ujson.loads(res.text)
        self.assertEqual(res.status, 200)

    def test_get_users(self):
        data = {
            'name': 'test2',
            'age': 3,
            'city_id': 1,
            'role_id': 1
        }
        res = self.client.create_user(data=data)
        body = ujson.loads(res.text)
        self.assertEqual(res.status, 200)
        res = self.client.get_users()
        body = ujson.loads(res.text)
        self.assertEqual(res.status, 200)
        self.assertGreaterEqual(len(body['data']), 1)

    def test_get_user(self):
        data = {
            'name': 'test3',
            'age': 3,
            'city_id': 1,
            'role_id': 1
        }
        res = self.client.create_user(data=data)
        body = ujson.loads(res.text)
        self.assertEqual(res.status, 200)
        res = self.client.get_user(id=body['data']['id'])
        body = ujson.loads(res.text)
        self.assertEqual(res.status, 200)
        self.assertEqual(body['data']['name'], 'test3')
        self.assertEqual(body['data']['city_id']['id'], 1)
