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

def get_posts(limit, offset): # Querys DB
    limit = int(limit)
    offset = int(offset)
    page = db.GqlQuery("SELECT * FROM NewPost ORDER BY created DESC LIMIT {} OFFSET {}".format(limit, offset))
    return page

class Handler(webapp2.RequestHandler): # Builds the Ancestor Handler
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class NewPost(db.Model): # Database Buildingblocks
    title = db.StringProperty(required = True)
    post_text = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler): #First Landing Page
    def get(self):
        self.redirect("/blog")

class ManyPostHandler(Handler):# MAIN PAGE with 5 posts per page
    def render_front(self, title="", post_text="", previous_link="", next_link=""):
        get_page = self.request.get("page")
        if get_page:
            get_page = int(get_page)
            offset = (get_page * 5) - 5
            posts = get_posts(5, offset)
            self.render("front.html", title=title, post_text=post_text, posts=posts, previous_link=previous_link, next_link=next_link)
        else:
            offset = 0
            self.redirect("blog?page=1")

    def get(self):
        get_page = self.request.get("page")
        if get_page:
            get_page = int(get_page)
            offset = (get_page * 5) - 5
            page_size = 5
            p = NewPost.all()
            total_posts = p.count()
            # all_posts = db.GqlQuery("SELECT * FROM NewPost")
            # total_posts = all_posts.count(offset)
            next_page = get_page + 1
            prev_page = get_page - 1
# q = Person.all()
# q.filter("last_name =", "Smith")
# q.filter("height <=", max_height)
# q.order("-height")

        else:
            get_page = 1
            offset = (get_page * 5) - 5
            page_size = 5
            p = NewPost.all()
            total_posts = p.count()
            # all_posts = db.GqlQuery("SELECT * FROM NewPost")
            # total_posts = all_posts.count(offset)
            next_page = get_page + 1
            prev_page = get_page - 1

        if total_posts > offset and get_page == 1:
            previous_link = '<span id="off"><<< Previous </span>'
            next_link = '<a href="/blog?page={}"> Next >>></a>'.format(next_page)
            self.render_front(previous_link=previous_link, next_link=next_link)

        elif total_posts > (offset + 5) and get_page > 1:
            previous_link = '<a href="/blog?page={}"><<< Previous </a>'.format(prev_page)
            next_link = '<a href="/blog?page={}"> Next >>></a>'.format(next_page)
            self.render_front(previous_link=previous_link, next_link=next_link)

        elif total_posts < (offset +5) and get_page > 1:
            previous_link = '<a href="/blog?page={}"><<< Previous </a>'.format(prev_page)
            next_link = '<span id="off"> Next >>></span>'
            self.render_front(previous_link=previous_link, next_link=next_link)

        elif total_posts <= 5:
            previous_link = '<span id="off"><<< Previous </span>'
            next_link = '<span id="off"> Next >>></span>'
            self.render_front(previous_link=previous_link, next_link=next_link)

class ViewPostHandler(Handler): # SINGLE POST PAGE
    def render_single(self, id):
        id = int(id)
        single_post = NewPost.get_by_id(id)
        self.render("single.html", single_post=single_post)


    def get(self, id):
        self.render_single(id)


class NewPostHandler(Handler): # NEW POST PAGE
    def render_new(self, title="", post_text="", error=""):
        self.render("newpost.html", title=title, post_text=post_text, error=error)

    def render_single(self, id):
        id = int(id)
        single_post = NewPost.get_by_id(id)
        self.render("single.html", single_post=single_post)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        post_text = self.request.get("post_text")

        if title and post_text:
            full_post = NewPost(title=title, post_text=post_text)
            full_post.put()

        else:
            error = "We need both a title and a post!"
            return self.render_new(title, post_text, error)

        new_id = full_post.key().id()
        self.render_single(new_id)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', ManyPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/newpost', NewPostHandler)
], debug=True)





#ids = self.request.get('id')
