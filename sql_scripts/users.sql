CREATE TABLE users (
	user_id SERIAL PRIMARY KEY,
	username VARCHAR(50) NOT NULL UNIQUE,
	fname VARCHAR(50) NOT NULL,
	lname VARCHAR (50),
	user_uuid uuid DEFAULT uuid_generate_v4(),
	email TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT NOW()
);


