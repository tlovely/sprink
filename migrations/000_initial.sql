create table migrations (
	current text,
	name text
);

insert into migrations values ( null, null );

create table schedule (
	id integer primary key autoincrement,
	cron text,
	duration integer not null,
	zones text not null,
	disabled integer not null,
	created integer not null,
	updated integer not null
);

insert into schedule ( duration, zones, disabled, created, updated ) values ( 1, '[]', -1, 0, 0 );

create table zone_state (
	id integer primary key autoincrement,
	zone integer not null,
	start integer not null,
	end_ integer
);

create table user (
	id integer primary key autoincrement,
	username text unique not null,
	password_hash text not null,
	token text
)