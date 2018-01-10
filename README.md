# Logs Analysis

---
## Overview
This is a project for the Udacity Full Stack Web Developer Nanodegree.

Using python, a logs analysis program is written to extract reports from a PostgreSQL database.


#### Investigation of table, using psql

##### <u><b> Database tables</b></u>
The database includes three tables:
- The authors table includes information about the authors of articles.
- The articles table includes the articles themselves.
- The log table includes one entry for each time a user has accessed the site.

This can be verified with the psql command:

news=> \dt

 Schema |   Name   | Type  |  Owner  
--------|----------|-------|---------
 public | articles | table | vagrant
 public | authors  | table | vagrant
 public | log      | table | vagrant

##### <u><b> Table 'authors' </b></u>
The columns in this can be verified with the psql command:

news=> \d authors

 Column |  Type   |                      Modifiers
--------|---------|------------------------------------------------------
 name   | text    | not null
 bio    | text    |
 id     | integer | not null default nextval('authors_id_seq'::regclass)

Indexes:
- "authors_pkey" PRIMARY KEY, btree (id)

Referenced by:
- TABLE "articles" CONSTRAINT "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)

##### <u><b> Table 'articles' </b></u>
The columns in this can be verified with the psql command:

news=> \d articles

 Column |           Type           |                       Modifiers
--------|--------------------------|--------------------------------
 author | integer                  | not null
 title  | text                     | not null
 slug   | text                     | not null
 lead   | text                     | 
 body   | text                     | 
 time   | timestamp with time zone | default now()
 id     | integer                  | not null default nextval('articles_id_seq'::regclass)
Indexes:
- "articles_pkey" PRIMARY KEY, btree (id)
- "articles_slug_key" UNIQUE CONSTRAINT, btree (slug)

Foreign-key constraints:
- "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)


##### <u><b> Table 'log' </b></u>
The columns in this can be verified with the psql command:

news=> \d log

 Column |           Type           |                       Modifiers
--------|--------------------------|--------------------------------
 path   | text                     |
 ip     | inet                     |
 method | text                     |
 status | text                     |
 time   | timestamp with time zone | default now()
 id     | integer                  | not null default nextval('log_id_seq'::regclass)
Indexes:
- "log_pkey" PRIMARY KEY, btree (id)

#### Query 1: What are the most popular three articles of all time?
Which articles have been accessed the most? Present this information as a sorted list with the most popular article at the top.

The query is done in function query_1 and results in:

```
Query 1: The most popular three articles of all time

              Title              |  Views
------------------------------------------
Candidate is jerk, alleges rival | 338647
Bears love berries, alleges bear | 253801
Bad things gone, say good people | 170098
```

#### Query 2: Who are the most popular article authors of all time?
That is, when you sum up all of the articles each author has written, which authors get the most page views? Present this as a sorted list with the most popular author at the top.

The query is done in function query_2 and results in:

```
Query 2: The most popular authors of all time

         Author        |  Views
--------------------------------
Ursula La Multa        | 507594
Rudolf von Treppenwitz | 423457
Anonymous Contributor  | 170098
Markoff Chaney         | 84557
```


#### Query 3: On which days did more than 1% of requests lead to errors?
The log table includes a column status that indicates the HTTP status code that the news site sent to the user's browser.

The query is done in function query_3 and results in:

```
Query 3: The days when more than 1% of requests failed

    Date   |  % failed
----------------------
2016-07-17 | 2.26 
```

#### Usage

1. Clone the project repository
```bash
git clone https://github.com/ArjaanBuijk/FullstackND-Logs-Analysis
```

2. Prepare the vagrant environment and PostgreSQL database

 The code was created and tested within a vagrant virtual machine against a PostgreSQL database.

 The vagrant virtual machine is set up as described [here](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/bc51d967-cb21-46f4-90ea-caf73439dc59/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0). his will give you the PostgreSQL database called 'news' and support software needed for this project.

 After installation of the vagrant VM, issue these commands:
```bash
vagrant up
vagrant ssh
cd /vagrant
```
 A file newsdata.sql is provided in newsdata.zip in the project repository, and must be copied into the vagrant folder, so it is accessible within the vagrant VM.

 The database is then filled with data using this command:
```bash
psql -d news -f newsdata.sql
```


3. Run with python3 within the vagrant VM with database in same folder.
(Both VM & Database are provided by Udacity in the Fullstack ND course instructions)
```bash
python logs_analysis.py
```
