BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "group" (
	"group_id"	INTEGER NOT NULL,
	"member"	INTEGER NOT NULL,
	PRIMARY KEY("group_id"),
	FOREIGN KEY("member") REFERENCES "users"("user_id")
);
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
	"car_name"	TEXT NOT NULL,
	PRIMARY KEY("car_id" AUTOINCREMENT)
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
	FOREIGN KEY("group_id") REFERENCES "group"("group_id"),
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
INSERT INTO "customers" VALUES (100,'R+B Technik');
INSERT INTO "customers" VALUES (1532,'Rügenwalder');
INSERT INTO "projects" VALUES (0,'k.A.',0);
INSERT INTO "projects" VALUES (1571,'Jotun Premix-Bereich',100);
INSERT INTO "projects" VALUES (1572,'P.A. Jansen',100);
INSERT INTO "projects" VALUES (1573,'Test-P2',1532);
INSERT INTO "users" VALUES (12,'Tim','XY.','Elektriker');
INSERT INTO "users" VALUES (16,'Sabrina','Miraglia','Büro');
INSERT INTO "users" VALUES (1001,'Franco','Miraglia','Büro');
INSERT INTO "users" VALUES (1029,'Marc','Rönick','Büro');
INSERT INTO "users" VALUES (8004,'Timo','Wohltorf','Büro');
INSERT INTO "users" VALUES (8012,'Igor','Giswein','Elektriker');
INSERT INTO "users" VALUES (8017,'Raphael','Schlameuß','Büro');
INSERT INTO "users" VALUES (8025,'Jenris','Pfabe','Büro');
INSERT INTO "users" VALUES (8039,'Frank','Böttcher','Büro');
INSERT INTO "users" VALUES (8057,'Michael','van Hoorn','Elektriker');
INSERT INTO "users" VALUES (8062,'Matthias','Korn','Büro');
INSERT INTO "users" VALUES (8066,'Marcel','Krüger','Elektriker');
INSERT INTO "users" VALUES (8067,'Horst','Wendelken','Schlosser');
INSERT INTO "users" VALUES (8070,'Thorsten','Flathmann','Schlosser');
INSERT INTO "users" VALUES (8078,'Sinan','Morina','Hauswart');
INSERT INTO "users" VALUES (8079,'Frank','Moser','Büro');
INSERT INTO "users" VALUES (8083,'Szymon','Minda','Dreher & Fräser');
INSERT INTO "users" VALUES (8085,'Albert','Litau','Schlosser');
INSERT INTO "users" VALUES (8108,'Adama','Barry','Schlosser');
INSERT INTO "users" VALUES (8109,'Timo','B.','Schlosser');
INSERT INTO "users" VALUES (8110,'Daniel','Maul','Büro');
INSERT INTO "users" VALUES (8113,'Ray','John','Elektriker');
INSERT INTO "users" VALUES (8114,'Hans-Peter','Schoof','Dreher & Fräser');
INSERT INTO "users" VALUES (8116,'Daniel','X.','Schlosser');
INSERT INTO "users" VALUES (12345,'Matthias','Gerke','Freie Mitarbeiter');
INSERT INTO "cars" VALUES (0,'Kein Auto');
INSERT INTO "cars" VALUES (1,'T11 HB-BE 384');
INSERT INTO "cars" VALUES (2,'T13 HB-SL 344');
INSERT INTO "cars" VALUES (3,'T14 HB-SL 554');
INSERT INTO "cars" VALUES (4,'T15 HB-SL 25');
INSERT INTO "cars" VALUES (5,'BMW HB-SL 133');
INSERT INTO "assignment_table" VALUES (21,8066,0,1572,'2024-03-04','2024-03-08',2024,'no','no','no','iF',0,'Schaltschrank',0,'P.A. Jansen');
INSERT INTO "assignment_table" VALUES (22,8057,0,1573,'2024-03-07','2024-03-08',2024,'ST.','H','T','vO',0,'Installation',0,'Test-P2');
INSERT INTO "assignment_table" VALUES (23,12,0,1571,'2024-03-05','2024-03-08',2024,'no','no','no','iF',0,'',0,'Jotun Premix-Bereich');
INSERT INTO "extras" VALUES ('ST.','Stundenzettel');
INSERT INTO "extras" VALUES ('H','Hotel');
INSERT INTO "extras" VALUES ('T','Telefon');
COMMIT;
