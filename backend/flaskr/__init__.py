import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate(request, selections):
  page = request.args.get('page', 1, type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start+QUESTIONS_PER_PAGE 
  
  questions = [question.format() for question in selections]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app, resources={"/": {"origins": "*"}})

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, PUT, POST, DELETE, OPTIONS')
    return response

  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def show_categories():
    #get all the categories from the database
    all_categories = Category.query.all()
    categories_dict = {}
    for category in all_categories:
      categories_dict[category.id] = category.type

    if len(all_categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories_dict
    })

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def show_questions():
    # retrieve all questions from the database
    all_questions = Question.query.all()
    total_questions = len(all_questions)
    #paginate the collected questions
    paginated_questions = paginate(request, all_questions)

    # retrieve all categories from database
    all_categories = Category.query.all()
    categories_dict = {}
    for category in all_categories:
        categories_dict[category.id] = category.type

    # throw 404 error if no questions are retrieved
    if (len(paginated_questions) == 0):
        abort(404)


    
    return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': total_questions,
        'categories': categories_dict
    })

  '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['GET','DELETE'])
  def delete_question(id):
    

    try:
      question = Question.query.get(id)

      if question is None:
        abort(404)

      question.delete()
      
      return jsonify({
        'success': True,
        'deleted': id
      })
    except:
      abort(422)

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():

    question_data = request.get_json()

    the_question = question_data['question']
    the_answer = question_data['answer']
    the_category = question_data['category']
    the_difficulty = question_data['difficulty']
    

    question = Question(
      question = the_question,
      answer = the_answer,
      category=the_category,
      difficulty=the_difficulty
    )
    #insert the new question into the database
    question.insert()
  
    all_questions = Question.query.all()
    paginated_questions = paginate(request, all_questions)

    return jsonify({
      'success': True,
      'created': question.id,
      'questions': paginated_questions,
      'total_questions': len(all_questions)
    })

  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start.
  '''
  @app.route('/questions/search', methods=['GET','POST'])
  def search_questions():
    
    body = request.get_json()

    if(body.get('searchTerm')):
      search_term = body.get('searchTerm')

    questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    
    if questions==[]:
      abort(404)

    results = paginate(request, questions)

    return jsonify({
      'success': True,
      'questions': results,
      'total_questions': len(questions)
    })

  ''' 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
   
  @app.route("/categories/<int:id>/questions")
  def show_questions_by_category(id):
        # retrive the category by given id
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            # retrive all questions in a category
            all_questions = Question.query.filter_by(category=str(id)).all()
            paginated_questions = paginate(request, all_questions)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(all_questions),
                'current_category': category.type
            })
        
        else:
            abort(404) 

  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
  
    body = request.get_json()

    category = body.get('quiz_category')
    previous_questions = body.get('previous_questions')

    
    if category['id'] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=category['id']).all()


    next_question = random.choice(questions).format()

    is_question_old = False
    if next_question['id'] in previous_questions:
      is_question_old = True

    while is_question_old:
      next_question = random.choice(questions).format()

      if (len(previous_questions) == len(questions)):
        return jsonify({
          'success': True,
          'message': "game over"
          }), 200

    return jsonify({
    'success': True,
    'question': next_question
    })

  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Sorry, bad request'
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Sorry, Resource not found'
    }), 404

  @app.errorhandler(422)
  def syntax_error(error):
    return jsonify({
      'success': False,
      'error': 422, 
      'message': 'Sorry, failed to process request. Check your syntax.'
    }), 422

  @app.errorhandler(500)
  def internal_server(error):
    return jsonify({
      'success': False,
      'error': 500, 
      'message': 'Sorry, the server is down. Please try again later.'
    }), 500

  return app