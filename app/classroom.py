from .post import Post

class Classroom:
    name=""
    posts=[]
    def __init__(self, title):
        self.name = title
    def addPost(self, post):
        self.posts.append(post)
    def getPost(self, i):
        return self.posts[i]