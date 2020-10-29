from flask import *
from flask_sqlalchemy import SQLAlchemy

route = '/v1'
app = Flask(__name__)
# DB settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{passwd}@{host}/{db}'.format(
    user='user',
    passwd='password',
    host='0.0.0.0',
    port='5432',
    db='database')
db = SQLAlchemy(app)


# models
class Video(db.Model):
    __tablename__ = 'videos'

    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String)
    description = db.Column(db.String)
    width = db.Column(db.String)
    height = db.Column(db.String)
    created_on = db.Column(db.String)
    path = db.Column(db.String)

    def __init__(self, title, description, w, h, ts, path):
        self.title = title
        self.description = description
        self.width = w
        self.height = h
        self.created_on = ts
        self.path = path


# views
@app.route(route + '/videos', methods=['GET'])
def list_videos():
    """
    This method return a list of 100 latest videos posted in db
    :return:
    """
    return make_response({'msg': 'ok'})


@app.route(route + 'videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """
    :param video_id: <int> you can get it by listing videos first
    :return: returns binary file containing video
    """
    return make_response({'msg': 'ok'})


@app.route(route + 'videos', methods=['POST'])
def upload_video():
    """
    :return: returns ok message and video_id
    """
    return make_response({'msg': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
