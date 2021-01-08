from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import requests
import datetime
import string
import random

# logging imports
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.handler import LogstashFormatter


route = '/v1'
app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})
# DB settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URI']
app.config['USERS_API_URI'] = 'http://users-api:8080/v1' # environ['USERS_API_URI'] 

db = SQLAlchemy(app)

# getting media directory ready
app.config['MEDIA_DIR'] = './media/'
if not os.path.exists(app.config['MEDIA_DIR']):
    os.mkdir(app.config['MEDIA_DIR'])

# -------------------------------------------
# Logging setup
# -------------------------------------------
# Create the logger and set it's logging level
logger = logging.getLogger("logstash")
logger.setLevel(logging.INFO)        

log_endpoint_uri = str(os.environ["LOGS_URI"]).strip()
log_endpoint_port = int(os.environ["LOGS_PORT"].strip())


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

    def __init__(self, user_id, title, description, w, h, path):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.width = w
        self.height = h
        self.created_on = str(datetime.datetime.utcnow())
        self.path = path

    def to_dict(self):
        tmp = {'title': self.title,
               'user_id': self.user_id,
               'description': self.description,
               'width': self.width,
               'height': self.height,
               'created_on': self.created_on,
               'path': self.path,
               'video_id': self.video_id}
        return tmp

# functions
def generate_request_id():
    return ''.join(random.choice(string.ascii_letters) for x in range(10))
 

# views
@app.route(route + '/videos/list', methods=['GET'])
def list_videos():
    """
    This method return a list of 100 latest videos posted in db
    :return:
    """
    request_id = None
    if 'X-Request-ID' in request.headers:
        request_id = request.headers.get('X-Request-ID')
    
    videos = Video.query.all()
    print(videos)
    logger.info("[videos-api][{}] listing latest videos".format(request_id))

    return make_response({'msg': 'ok', 'content': [i.to_dict() for i in videos]})


@app.route(route + '/videos/list/<int:user_id>', methods=['GET'])
def list_user_videos(user_id):
    """
    This method return a list of 100 latest user videos posted in db
    :return:
    """
    request_id = None
    if 'X-Request-ID' in request.headers:
        request_id = request.headers.get('X-Request-ID')

    videos = Video.query.filter_by(user_id=user_id).all()
    print(videos)
    logger.info("[videos-api][{}] listing user videos".format(request_id))
    return make_response({'msg': 'ok', 'content': [i.to_dict() for i in videos]})



@app.route(route + '/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """
    :param video_id: <int> you can get it by listing videos first
    :return: returns binary file containing video
    """
    video = Video.query.filter_by(video_id=int(video_id)).first()
    logger.info("[users-api] serving video")
    return make_response({'msg': 'ok', 'content': video.to_dict()})


def generate_filename(filename, stringLength=20):
    extension = filename.split('.')[-1]
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength)) + '.' + extension


@app.route(route + '/videos', methods=['POST'])
def upload_video():
    """
    :return: returns ok message and video_id
    """
    request_id = generate_request_id()

    token = request.headers.get('Authorization')
    logger.info("[videos-api][{}] we are getting a new video".format(request_id))

    user_id = requests.get(app.config['USERS_API_URI'] + '/user/check', headers={'Authorization': token, 'X-Request-ID': request_id}).json()['user_id']
    video_title = request.form.get('title')
    video_description = request.form.get('description') 
    file_content = request.files.get('file', None)

    current_chunk = int(request.form.get('current_chunk'))
    chunk_count = int(request.form.get('chunk_count', None))
    chunk_offset = int(request.form.get('chunk_offset', None))
    
    filename = file_content.filename
    file_path = os.path.join(app.config['MEDIA_DIR'], filename)

    with open(file_path, 'ab') as f:
        f.seek(chunk_offset)
        f.write(file_content.stream.read())

    if current_chunk != chunk_count:
        # uploading
        return make_response({'msg': 'ok', 'current_chunk': current_chunk, 'chunk_count': chunk_count})
    else:
        # finish upload
        video = Video(user_id, video_title, video_description, 0, 0, file_path)
        db.session.add(video)
        db.session.commit()
        video = Video.query.filter_by(user_id = user_id, title = video_title, description = video_description).first()
        return make_response({'msg': 'ok', 'video_id': video.video_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
