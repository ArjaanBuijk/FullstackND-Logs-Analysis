#!/usr/bin/env python3
"""Logs analysis of news database"""
import psycopg2


DBNAME = "news"


def query_1():
    """Returns a sorted list of the most popular three articles of all time,
       with the most popular article at the top."""
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()

    # temporary view to select the top 3 articles from the log table
    # include only valid requests from the log table
    sql_str = """CREATE TEMP VIEW tmp_top3
                 AS
                 SELECT path, count(*) AS num
                 FROM log WHERE path LIKE '/article/%' and status LIKE '%200%'
                 GROUP BY path
                 ORDER BY num
                 DESC LIMIT 3;"""

    # temporary view to convert the path of the top 3 articles into the slug
    # this will allow joining to the articles table, using slug as the key
    sql_str += """CREATE TEMP VIEW tmp_top3_slugs
                  AS
                  SELECT REPLACE(path,'/article/','') AS slug, *
                  FROM tmp_top3;"""

    # get the title of the top 3 articles by joining with the articles table
    sql_str += """SELECT articles.title, tmp_top3_slugs.num
                 FROM articles
                 JOIN tmp_top3_slugs
                 ON articles.slug = tmp_top3_slugs.slug
                 GROUP BY articles.title, tmp_top3_slugs.num
                 ORDER BY tmp_top3_slugs.num DESC;"""

    c.execute(sql_str)
    q = c.fetchall()
    db.close()
    return q


def query_2():
    """Returns a sorted list of the most popular authors of all time,
       with the most popular author at the top."""
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()

    # temporary view to aggregate the views per article from the log table
    # convert path into slug, to allow joining with articles table
    sql_str = """CREATE TEMP VIEW tmp_1
                 AS
                 SELECT REPLACE(path,'/article/','') AS slug, count(*) AS num
                 FROM log
                 WHERE path LIKE '/article/%'
                 GROUP BY path
                 ORDER BY num;"""

    # temporary view to aggregrate the views per author (it's id)
    sql_str += """CREATE TEMP VIEW tmp_2
                  AS
                  SELECT articles.author, sum(tmp_1.num) AS num
                  FROM articles
                  JOIN tmp_1
                  ON articles.slug = tmp_1.slug
                  GROUP BY articles.author ORDER BY num DESC;"""

    # get the name of the authors in order of popularity
    sql_str += """SELECT authors.name, tmp_2.num
                 FROM authors
                 JOIN tmp_2
                 ON authors.id = tmp_2.author
                 GROUP BY authors.name, tmp_2.num
                 ORDER BY tmp_2.num DESC;"""

    c.execute(sql_str)
    q = c.fetchall()
    db.close()
    return q


def query_3():
    """Returns a sorted list of the days where more than 1% of requests failed
       with the day with most failed reques at the top."""
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()

    # temporary view to extract the date from time column
    sql_str = """CREATE TEMP VIEW tmp_1
                 AS
                 SELECT CAST(time AS DATE) as date, status
                 FROM log;"""

    # temporary view to aggregate the successful views per day
    sql_str += """CREATE TEMP VIEW tmp_200
                 AS
                 SELECT date, count(*)
                 AS s200
                 FROM tmp_1
                 WHERE status LIKE '%200%'
                 GROUP BY date;"""

    # temporary view to aggregate the failed views per day
    sql_str += """CREATE TEMP VIEW tmp_404
                 AS
                 SELECT date, count(*)
                 AS s404
                 FROM tmp_1
                 WHERE status LIKE '%404%'
                 GROUP BY date;"""

    # temporary view to calculate total number of failures per day
    # use a left join on tmp_404 to include only the days with failures
    sql_str += """CREATE TEMP VIEW tmp_total
                  AS
                  SELECT tmp_404.date, tmp_404.s404, tmp_200.s200,
                         tmp_404.s404+tmp_200.s200 AS total
                  FROM tmp_404
                  LEFT JOIN tmp_200
                  ON tmp_404.date = tmp_200.date;"""

    # temporary view to calculate percentage of failures per day
    sql_str += """CREATE TEMP VIEW tmp_percentage
                  AS
                  SELECT date, 100.0*s404/total
                  AS percentage
                  FROM tmp_total;"""

    # get the days where more than 1 percentage failed in order of failures
    # for pretty printing, use only 2 digits after decimal point.
    sql_str += """SELECT date, CAST(percentage AS DECIMAL(16,2))
                  FROM tmp_percentage
                  WHERE percentage > 1.0
                  ORDER BY percentage desc;"""

    c.execute(sql_str)
    q = c.fetchall()
    db.close()
    return q


def print_sql_query(title, headings, q):
    """Prints a nice table with title and heading

    Args:
        title (string) : the title of the query
        headings (tuple of strings) : the column headings
        q (list of tuples) : the result of an SQL query we want to print
    """

    print(' ')
    print('='*80)
    print(title)
    print(' ')

    data = [headings] + q

    # determine column widths
    pad = 1
    widths = [pad]*len(headings)  # include 1 space padding at end
    for row in data:
        for i in range(len(headings)):
            widths[i] = max(widths[i], pad+len(str(row[i])))

    for i, d in enumerate(data):
        if i == 0:
            line = '| '.join(str(x).center(widths[ii])
                             for ii, x in enumerate(d))
            print(line)
            print('-' * len(line))
        else:
            line = '| '.join(str(x).ljust(widths[ii])
                             for ii, x in enumerate(d))
            print(line)


if __name__ == '__main__':
    print_sql_query('Query 1: The most popular three articles of all time',
                    ('Article', 'Views'),
                    query_1())

    print_sql_query('Query 2: The most popular authors of all time',
                    ('Author', 'Views'),
                    query_2())

    print_sql_query('Query 3: The days when more than 1% of requests failed',
                    ('Date', '% failed'),
                    query_3())
