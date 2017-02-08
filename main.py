#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class NewPost(db.Model):
    title = db.StringProperty(required = True)
    post_text = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.redirect("/blog")

class ViewPostHandler(Handler):
    def render_front(self, title="", post_text=""):
        posts = db.GqlQuery("SELECT * FROM NewPost ORDER BY created DESC LIMIT 5 ")
        self.render("front.html", title=title, post_text=post_text, posts=posts)

    def get(self, id):
        if id:
            single_post = Post.get_by_id(id)
            self.render("single.html")
###ASK HOW TO MAKE THIS WORK IN SLACK TOMORROW GRRRRRRRRR
        else:
            self.render_front()

class NewPostHandler(Handler):
    def render_new(self, title="", post_text="", error=""):
        self.render("newpost.html", title=title, post_text=post_text, error=error)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        post_text = self.request.get("post_text")

        if title and post_text:
            full_post = NewPost(title=title, post_text=post_text)
            full_post.put()

            self.redirect("/blog")

        else:
            error = "We need both a title and a post!"
            self.render_new(title, post_text, error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/newpost', NewPostHandler)
], debug=True)
