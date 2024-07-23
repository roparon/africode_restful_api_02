from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api,Resource, reqparse, fields, marshal_with, abort
from datetime import datetime, timezone
app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    posts = db.relationship('PostModel', backref='author', lazy=True)
    def __repr__(self):
         return self.username

class PostModel(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     title = db.Column(db.String(80), nullable=False)
     content = db.Column(db.String(200), nullable=False)
     created_at = db.Column(db.DateTime, nullable=False, default = lambda: datetime.now(timezone.utc))
     user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)


     def __repr__(self):
          return self.title

users_args = reqparse.RequestParser()
users_args.add_argument('username', type=str, required=True, help = 'Username is required')


posts_args = reqparse.RequestParser()
posts_args.add_argument('title', type=str, required=True, help = 'Title is required')
posts_args.add_argument('content', type=str, required=True, help = 'Content is required')
posts_args.add_argument('user_id', type=int, required=True, help = 'User ID is required')


userfields = {
     
     "id": fields.Integer,
     "username": fields.String
}

postfields = {
     "id": fields.Integer,
     "title": fields.String,
     "content": fields.String,
     "created_at": fields.DateTime,
     "author": fields.String(attribute="author.username"),}


class Users(Resource):
     @marshal_with(userfields)
     def get(self):
          users = UserModel.query.all()
          return users, 200
     
    
     @marshal_with(userfields)
     def post(self):
          args = users_args.parse_args()
          username = args['username']
          new_user = UserModel(username=username)
          db.session.add(new_user)
          db.session.commit()
          return new_user, 201
     
     #get user

class User(Resource):
    @marshal_with(userfields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User doesn't exist")
        return user
        
        #update user
    @marshal_with(userfields)
    def patch(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User with ID (id) doesn't exist")
            return user
        args = users_args.parse_args()
        user.username = args['username']
        db.session.commit()
        return user, 200
    
    #delete user
    @marshal_with(userfields)
    def delete(self, id):
         user = UserModel.query.filter_by(id=id).first()
         if not user:
             abort(404, message="User with ID (id) doesn't exist")
             return user
         db.session.delete(user)
         db.session.commit()
         users = UserModel.query.all()
         return users, 200
    
class Posts(Resource):
     @marshal_with(postfields)
     def get(self):
          posts = PostModel.query.all()
          return posts, 200
     
     @marshal_with(postfields)
     def post(self):
          args = posts_args.parse_args()
          title = args['title']
          content = args['content']
          user_id = args['user_id']
          user = UserModel.query.get(user_id)
          if not user:
              return{"message":"user not found"}, 404
          new_post = PostModel(title=title, content=content,user_id=user_id)
          db.session.add(new_post)
          db.session.commit()
          return new_post, 201
     
class Post(Resource):
      @marshal_with(postfields)
      def get(self,id):
         post = PostModel.query.filter_by(id=id).first()
         if not post:
              abort(404, message="Post with ID (id) doesn't exist")
         return post, 200
      #update post
      @marshal_with(postfields)
      def patch(self, id):
           args = posts_args.parse_args()
           post = PostModel.query.filter_by(id=id).first()
           if not post:
              abort(404, message="Post with ID (id) doesn't exist")
           post.title = args['title']
           post.content = args['content']
           db.session.commit()
           return post, 200
      #delete post
      @marshal_with(postfields)
      def delete(self, id):
          post = PostModel.query.filter_by(id=id).first()
          if not post:
              abort(404, message="Post with ID (id) doesn't exist")
          db.session.delete(post)
          db.session.commit()
          posts = PostModel.query.all()
          return posts, 200
     

api.add_resource(Users, "/users/")
api.add_resource(User, "/users/<int:id>/")
api.add_resource(Posts, "/posts/")
api.add_resource(Post, "/posts/<int:id>/")
@app.route('/')
def home():
    return "Hello world!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
 