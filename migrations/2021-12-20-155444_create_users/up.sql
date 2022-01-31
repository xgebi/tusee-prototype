-- Your SQL goes here
CREATE TABLE IF NOT EXISTS tusee_users (
    user_uuid character varying(200) NOT NULL PRIMARY KEY,
	display_name text NOT NULL DEFAULT 'human',
	password character varying(500) NOT NULL,
	email character varying(350) UNIQUE NOT NULL ,
	token character varying(350) NOT NULL DEFAULT '',
	expiry_date double precision NOT NULL DEFAULT 0,
	first_login boolean NOT NULL DEFAULT TRUE,
	uses_totp boolean NOT NULL DEFAULT TRUE,
	totp_secret character varying(16) NOT NULL
)