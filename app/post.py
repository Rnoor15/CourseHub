class Post:
    comments = 0
    title = ""
    author = ""
    rating = 0
    def __init__(self, comments, title, author, rating):
        self.comments = comments
        self.title = title
        self.author = author
        self.rating = rating
    def incComments(self):
        self.comments+=1
    def decComments(self):
        self.comments-=1
    def incRating(self):
        self.rating+=1
    def decRating(self):
        self.rating-=1
        

        