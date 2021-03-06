import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from database.models import create_db, City, Rest
from dotenv import load_dotenv

load_dotenv()


class CapstoneTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "meal_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            os.getenv('USER'), os.getenv('PASSWORD'), 'localhost:5432', self.database_name)
        create_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """I am not using production database.
        So I do not need any lines here.
        """
        pass

    def test_a_404_get_all_cities(self):
        res = self.client().get('/cities')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'not found')

    def test_b_404_get_all_restaurants(self):
        res = self.client().get('/restaurants')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'not found')

    'while testing database is empty, two tests above work appropriately'

    def test_c_post_new_restaurant(self):
        res = self.client().post(
            '/restaurants',
            json={
                "name": "La Piola",
                "description": "Tasty plov",
                "city": "Tashkent"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['restaurant'])

    def test_d_get_all_cities(self):
        res = self.client().get('/cities')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['cities']))

    def test_e_get_all_restaurants(self):
        res = self.client().get('/restaurants')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['restaurants']))

    def test_f_get_restaurants_by_city(self):
        res = self.client().get('/cities/1/restaurants')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data["count"], 0)
        self.assertTrue(len(data['restaurants']))

    def test_g_update_restaurant(self):
        res = self.client().patch(
            '/restaurants/1',
            json={
                "name": "Buxoro cafe",
                "description": "uch etajlik",
                "city": "Buxoro"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["restaurant"])

    def test_h_delete_restaurant(self):
        res = self.client().delete('/restaurants/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['deleted'])

    def test_i_error_delete_restaurant(self):
        res = self.client().delete('/restaurants/99999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'not found')

    def test_j_error_post_new_restaurant(self):
        res = self.client().post('/restaurants', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_k_error_update_restaurant(self):
        res = self.client().patch(
            '/restaurants/52525252852',
            json={
                "name": "Buxoro cafe",
                "description": "uch etajlik",
                "city": "Buxoro"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'not found')

    def test_l_error_get_restaurants_by_city(self):
        res = self.client().get('/cities/9999999/restaurants')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
