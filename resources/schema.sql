-- Schema of a torianik_music database
-- Generated 2022-07-12
-- SQLAlchemy 1.4.39

CREATE TABLE IF NOT EXISTS artists (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)


;

CREATE TABLE IF NOT EXISTS tracks (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	artist_id VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(artist_id) REFERENCES artists (id)
)


;

CREATE TABLE IF NOT EXISTS playlists (
	id SERIAL NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)


;

CREATE TABLE IF NOT EXISTS edges (
	track_id VARCHAR NOT NULL, 
	playlist_id INTEGER NOT NULL, 
	PRIMARY KEY (track_id, playlist_id), 
	FOREIGN KEY(track_id) REFERENCES tracks (id), 
	FOREIGN KEY(playlist_id) REFERENCES playlists (id)
)


;
