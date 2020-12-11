from flask import *
from flask_sqlalchemy import SQLAlchemy
from os import environ

# logging imports
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.handler import LogstashFormatter


route = '/v1'
app = Flask(__name__)
# DB settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
    user='dbuser',
    passwd='postgres',
    host='0.0.0.0',
    port='5432',
    db='video-db')
"""
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DB_URI']
db = SQLAlchemy(app)


# -------------------------------------------
# Logging setup
# -------------------------------------------
# Create the logger and set it's logging level
logger = logging.getLogger("logstash")
logger.setLevel(logging.INFO)        

log_endpoint_uri = str(environ["LOGS_URI"]).strip()
log_endpoint_port = int(environ["LOGS_PORT"].strip())


# Create the handler
handler = AsynchronousLogstashHandler(
    host=log_endpoint_uri,
    port=log_endpoint_port, 
    ssl_enable=True, 
    ssl_verify=False,
    database_path='')

# Here you can specify additional formatting on your log record/message
formatter = LogstashFormatter()
handler.setFormatter(formatter)

# Assign handler to the logger
logger.addHandler(handler)




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

    def __init__(self, title, description, w, h, path):
        self.title = title
        self.description = description
        self.width = w
        self.height = h
        self.created_on = str(datetime.datetime.utcnow())
        self.path = path

    def to_dict(self):
        tmp = {'title': self.title,
               'description': self.description,
               'width': self.width,
               'height': self.height,
               'created_on': self.created_on}
        return tmp


# views
@app.route(route + '/videos/list', methods=['GET'])
def list_videos():
    """
    This method return a list of 100 latest videos posted in db
    :return:
    """
    videos = Video.query.all()
    print(videos)
    logger.info("200 - OK")

    return make_response({'msg': 'ok', 'content': [i.to_dict() for i in videos]})


@app.route(route + '/videos/list/<int:user_id>', methods=['GET'])
def list_user_videos(user_id):
    """
    This method return a list of 100 latest user videos posted in db
    :return:
    """
    videos = Video.query.filter_by(user_id=user_id).all()
    print(videos)
    logger.info("200 - OK")
    return make_response({'msg': 'ok', 'content': [i.to_dict() for i in videos]})



@app.route(route + '/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """
    :param video_id: <int> you can get it by listing videos first
    :return: returns binary file containing video
    """
    video = Video.query.filter_by(video_id=int(video_id)).first()
    logger.info("200 - OK")
    return make_response({'msg': 'ok', 'content': video.to_dict()})


@app.route(route + '/videos', methods=['POST'])
def upload_video():
    """
    :return: returns ok message and video_id
    """
    logger.info("200 - OK")
    return make_response({'msg': 'ok'})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
