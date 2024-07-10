BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "customers" (
	"customer_id"	INTEGER NOT NULL,
	"customer_name"	TEXT NOT NULL,
	PRIMARY KEY("customer_id")
);
CREATE TABLE IF NOT EXISTS "projects" (
	"project_id"	INTEGER NOT NULL,
	"project_name"	TEXT NOT NULL,
	"customer_id"	INTEGER NOT NULL,
	PRIMARY KEY("project_id"),
	FOREIGN KEY("customer_id") REFERENCES "customers"("customer_id")
);
CREATE TABLE IF NOT EXISTS "CalendarWeek" (
	"week_id"	INTEGER NOT NULL,
	"startDate"	DATE NOT NULL,
	"endDate"	DATE NOT NULL,
	"year"	INTEGER NOT NULL,
	PRIMARY KEY("week_id","year")
);
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER NOT NULL UNIQUE,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"work_field"	TEXT NOT NULL,
	PRIMARY KEY("user_id")
);
CREATE TABLE IF NOT EXISTS "cars" (
	"car_id"	INTEGER NOT NULL UNIQUE,
	"car_name"	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "meetings" (
	"meeting_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"date"	DATE NOT NULL,
	"startTime"	TIME NOT NULL,
	"endTime"	TIME NOT NULL,
	"room"	TEXT NOT NULL,
	"service"	INTEGER NOT NULL,
	"m_group"	INTEGER NOT NULL,
	PRIMARY KEY("meeting_id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "assignment_table" (
	"assignment_id"	INTEGER NOT NULL UNIQUE,
	"user_id"	INTEGER NOT NULL,
	"car_id"	INTEGER NOT NULL,
	"project_id"	INTEGER NOT NULL,
	"startDate"	DATE NOT NULL,
	"endDate"	DATE NOT NULL,
	"year"	DATE NOT NULL,
	"extra1"	TEXT NOT NULL,
	"extra2"	TEXT NOT NULL,
	"extra3"	TEXT NOT NULL,
	"ort"	TEXT NOT NULL,
	"group_id"	INTEGER NOT NULL,
	"hinweis"	TEXT NOT NULL,
	"abwesend"	INTEGER NOT NULL,
	"project_name"	TEXT NOT NULL,
	PRIMARY KEY("assignment_id" AUTOINCREMENT),
	FOREIGN KEY("car_id") REFERENCES "cars"("car_id"),
	FOREIGN KEY("project_name") REFERENCES "projects"("project_name"),
	FOREIGN KEY("project_id") REFERENCES "projects"("project_id"),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
	FOREIGN KEY("year") REFERENCES "CalendarWeek"("year")
);
CREATE TABLE IF NOT EXISTS "extras" (
	"id"	TEXT NOT NULL,
	"extra_name"	TEXT NOT NULL
);
INSERT INTO "customers" VALUES (0,'k.A.');
INSERT INTO "projects" VALUES (0,'k.A.',0);
INSERT INTO "cars" VALUES (0,'Kein Auto');
INSERT INTO "extras" VALUES ('ST.','Stundenzettel');
INSERT INTO "extras" VALUES ('H','Hotel');
INSERT INTO "extras" VALUES ('T','Telefon');
COMMIT;
