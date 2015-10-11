# import app engine libs
import sys
from os import path

sdk_path = 'C:\Program Files\Google\Cloud SDK\google-cloud-sdk'
sys.path.insert(1, path.join(sdk_path, 'platform/google_appengine'))
sys.path.insert(1, path.join(sdk_path, 'platform/google_appengine/lib/yaml/lib'))
sys.path.insert(1, 'myapp/lib')

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from main import app
import hamcrest as h
import json

def setUp():
    # First, create an instance of the Testbed class.
    tb= testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    tb.activate()
    # Next, declare which service stubs you want to use.
    tb.init_datastore_v3_stub()
    tb.init_memcache_stub()
    # Clear ndb's in-context cache between tests.
    # This prevents data from leaking between tests.
    # Alternatively, you could disable caching by
    # using ndb.get_context().set_cache_policy(False)
    ndb.get_context().clear_cache()

def test_hello():
    with app.test_client() as c:
        resp = c.post('/bot', data=dict(user_name='my_username', text='runbotton: hi', trigger_word='runbotton:'))
        h.assert_that(json.loads(resp.data), h.equal_to({'text': 'Hello, my_username'}))

def test_kyle():
  with app.test_client() as c:
      resp = c.post('/bot', data=dict(user_name='19letterslong', text='runbotton: hi', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': 'Kiss off, twit!'}))

def test_destroy():
  with app.test_client() as c:
      resp = c.post('/bot', data=dict(user_name='my_username', text='runbotton: destroy testcase', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': 'Launching ICBMs at testcase.'}))

def test_destroy_all():
  with app.test_client() as c:
      resp = c.post('/bot', data=dict(user_name='my_username', text='runbotton: destroy', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': 'Launching ICBMs at EVERYBODY.'}))

def test_love_q():
  with app.test_client() as c:
      resp = c.post('/bot', data=dict(user_name='my_username', text='runbotton: who do you love?', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': 'I will always love nobody!'}))

def test_love_q2():
  with app.test_client() as c:
      resp = c.post('/bot', data=dict(user_name='my_username', text='runbotton: love me', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': 'I will be yours until I die.'}))

      resp = c.post('/bot', data=dict(user_name='my_username', text='runbotton: who do you love?', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': 'I will always love my_username!'}))

      resp = c.post('/bot', data=dict(user_name='my_username2', text='runbotton: love me', trigger_word='runbotton:'))
      h.assert_that(json.loads(resp.data), h.equal_to({'text': "my_username is dead to me. I'm all about my_username2 now!"}))

