CREATE DATABASE video_db;
CREATE TABLE IF NOT EXISTS videos
(
	video_id serial PRIMARY KEY,
	user_id serial,
	title VARCHAR ( 100 ) UNIQUE NOT NULL,
	description VARCHAR ( 1000 ) NOT NULL,
	width INT NOT NULL,
	height INT NOT NULL,
	created_on TIMESTAMP NOT NULL,
	path VARCHAR ( 1000 ) UNIQUE NOT NULL
);
INSERT INTO videos (video_id, user_id, title, description, width, height, created_on, path) VALUES (1,1,'Video title', 'Video description', 1920, 1080, '2006-01-01 15:36:38', 'path/to/video/video.mp4');
