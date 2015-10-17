from flask import Flask, request, jsonify
import re
import json
import logging
import parse
from google.appengine.ext import ndb

log = logging.getLogger(__name__)


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
#@ndb.transactional
def bot_old():
    # prevents looping
    if request.form['user_name'] == 'slackbot': return jsonify()
    try:
        log.info('Form is %s' % request.form)
        user_name = request.form['user_name']
        trigger = request.form.get('trigger_word') or ''
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

        for r in Rule.query().iter():
            if not r.trigger_code.strip(): continue

            message = Message(request.form)
            match = re.compile(r.trigger_code).match(message.text)
            if match:
                context = {('group[%d]' % i): v for i, v in enumerate(match.groups())}
                context.update({
                  'text': message.text,
                  'user_name': message.user_name,
                })

                return jsonify({'text': parse.execute(r.action_code, parse.ParseContext(context))})

        return jsonify()
    except Exception as e:
        print "exception"
        if '__test' in request.form or request.form['__test']:
            return jsonify({'text': 'Error: %s' % e.message})
        return jsonify()

class Message(object):
    def __init__(self, form):
        self.user_name = form['user_name']
        self.trigger_word = form.get('trigger_word') or ''
        self.text = form['text'][len(self.trigger_word):].strip()
        self._words = None

    def words(self):
        if self._words is None:
            self._words = self.text.split()
        return self._words

    def word(self, n):
        return self.words()[n]


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

