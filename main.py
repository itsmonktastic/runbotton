from flask import Flask, request, jsonify
import re
import json
from google.appengine.ext import ndb


app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def hello():
    return app.send_static_file('index.html')

class Fact(ndb.Model):
  value = ndb.StringProperty()

@app.route('/bot', methods=['POST'])
@ndb.transactional
def bot_old():
    print request.form
    user_name = request.form['user_name']
    if user_name == '19letterslong':
        return jsonify(text='Kiss off, twit!')
    trigger = request.form['trigger_word']
    text = request.form['text'][len(trigger):].strip()

    if text.lower().startswith('hello') or text.lower().startswith('hi') or text.lower().startswith('greetings'):
        return jsonify(text='Hello, {}'.format(user_name))

    words = text.split()
    kill_words = 'destroy kill crush annihilate assassinate'.split()

    if len(words) > 0:
      for w in kill_words:
        if words[0].lower() == w:
          target = words[1] if len(words) > 1 else 'EVERYBODY'
          return jsonify(text='Launching ICBMs at {}.'.format(target))

    if 'love?' in text.lower().strip():
      current_love = 'nobody'
      love = Fact.get_by_id('love')
      if love is not None:
          current_love = love.value

      return jsonify(text='I will always love {}!'.format(current_love))

    if 'love me' in text.lower().strip():
      love = Fact.get_by_id('love')
      old_love = 'I will be yours until I die.'

      if love is not None:
        old_love = "{} is dead to me. I'm all about {} now!".format(love.value, user_name)
      else:
        love = Fact(id='love')

      love.value = user_name
      love.put()
      return jsonify(text=old_love)

    return jsonify()

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

class Rule(ndb.Model):
  trigger_code = ndb.StringProperty()
  action_code = ndb.StringProperty()

def rule_code_dict(rule):
  return {'id': rule.key.integer_id(), 'triggerCode': rule.trigger_code, 'actionCode': rule.action_code}

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    if request.method == 'POST':
        r = Rule(trigger_code='', action_code='')
        r.put()
        return json.dumps(rule_code_dict(r))
    return json.dumps([rule_code_dict(r) for r in Rule.query().iter()])

@app.route('/rules/<int:rule_id>', methods=['POST'])
def rule(rule_id):
    r = Rule.get_by_id(rule_id)
    r.populate(trigger_code=request.form['triggerCode'], action_code=request.form['actionCode'])
    r.put()
    return json.dumps(rule_code_dict(r))

