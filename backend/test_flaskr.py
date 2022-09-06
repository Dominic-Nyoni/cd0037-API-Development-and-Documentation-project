import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def get_categories_test(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)
        self.assertTrue(data.get('categories'))
    
    def paginate_test(self):
        res = self.client().get('/questions')
        data = json.loads(res.set_data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('success'), True)
        self.assertTrue(data.get('questions'))

    def invalid_page_numbers_test(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        
        self.assertEqual(data.get('error'), 404)
        self.assertEqual(data.get('success'), False)
    
    def delete_questions_test(self):
        res = self.client().delete('questions/11')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 11)

    def search_question_test(self):
        res = self.client().post('questions/search', json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def invalid_search_input_test(self):
        res = self.client().post('questions/search', json={"searchTerm": "hakuna matata"})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Sorry,Resource not found")

    def create_question_test(self):
        new_question = {
        'question': 'How many US States are there?',
        'answer': '50',
        'category': '1',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
    
    def create_question_failed_test(self):
        bad_question = {
        'question': 'How many letters are in the alphabet?',
        'category': '1',
        'answer':'',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=bad_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Sorry, failed to process request. Check your syntax.")

    def invalid_category_test(self):
        res = self.client().get('categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

    def play_quiz_test(self):
        input_data = {
            'previous_questions':[2, 6],
            'quiz_category': {
                'id': 5,
                'type': 'Entertainment'
            }
        }

        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 6)

        self.assertEqual(data['question']['category'], 5)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()