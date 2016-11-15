"""
Creates a sqlite database with tables and data, and runs a server.
Just run this script and point your prowser to http://localhost:5000

TODO: Include this to run with virtualenv
activate_this = '/path/to/env/bin/activate_this.py'
with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))
"""
from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine('sqlite:///testquiz.db')
Base = declarative_base()


class Question(Base):
    __tablename__ = 'question'
    # implicit autoincrement for sqlite
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    intro = Column(String(250), nullable=False)
    # TODO: allow for multiple correct answers
    correct = Column(String(80), nullable=False)

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


# create tables
Base.metadata.bind = engine
Base.metadata.drop_all()
Base.metadata.create_all()

Session = sessionmaker(engine)
session = Session()

# populate tables, e.g. via json
questions = [{'name': 'hello world',
              'intro': "If a = 'hello world', how do you print that?",
              'correct': 'print(a)'},
             {'name': 'sum',
              'intro': "If x = 7 and y = 3, how do you get the sum of the two?",
              'correct': 'x+y'}]

for q in questions:
    x = Question(**q)
    session.add(x)
session.commit()


@app.route('/')
def list_questions():
    questions = session.query(Question).all()
    return render_template('list_questions.html', questions=questions)


class AnswerForm(FlaskForm):
    answer = StringField('Answer')


@app.route('/question/<int:question_id>/ask', methods=['GET', 'POST'])
def ask_question(question_id):
    question = session.query(Question).get(question_id)
    form = AnswerForm()
    if form.validate_on_submit():
        user_answer = form.answer.data
        return redirect(url_for('feedback',
                                question_id=question_id,
                                user_answer=user_answer))
    return render_template('ask_question.html',
                           question=question,
                           form=form)


@app.route('/question/<int:question_id>/askagain', methods=['GET', 'POST'])
def askagain_question(question_id):
    user_answer = request.args.get('user_answer')
    question = session.query(Question).get(question_id)
    form = AnswerForm()
    if form.validate_on_submit():
        user_answer = form.answer.data
        return redirect(url_for('feedback',
                                question_id=question_id,
                                user_answer=user_answer))
    return render_template('askagain_question.html',
                           question=question,
                           form=form,
                           user_answer=user_answer)


@app.route('/question/<int:question_id>/feedback', methods=['GET', 'POST'])
def feedback(question_id):
    user_answer = request.args.get('user_answer')
    question = session.query(Question).get(question_id)
    if user_answer == question.correct:
        return render_template('feedback.html',
                               question=question,
                               user_answer=user_answer)
    return redirect(url_for('askagain_question',
                            question_id=question_id,
                            user_answer=user_answer))


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'NOTTHATSECRET'
    app.run(host='0.0.0.0', port=8000)
