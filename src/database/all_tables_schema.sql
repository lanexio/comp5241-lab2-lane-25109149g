CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
CREATE TABLE note (
	id INTEGER NOT NULL, 
	title VARCHAR(120) NOT NULL, 
	content TEXT, 
	timestamp DATETIME, 
	PRIMARY KEY (id)
);
