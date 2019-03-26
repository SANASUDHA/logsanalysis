# !/usr/bin/env python

import psycopg2

# Connect to the database to extract query results

db = psycopg2.connect(dbname="news")
c = db.cursor()


""" preparing queries for getting most popular 3 articles of all
time from news database"""

my_query_1 = ("""select title,count(*) from log, articles
                 where articles.slug = substring(path, 10)
                 group by substring(path,10), title
                 order by count(*) desc limit 3; """)


""" preparing queries for getting most popular article authors of all
time from news database"""

my_query_2 = """select authors.name, count(*) as num
            from articles, authors, log
            where log.status='200 OK'
            and authors.id = articles.author
            and articles.slug = substr(log.path, 10)
            group by authors.name
            order by num desc;
            """


""" preparing queries for getting the date on which day we got the more
than 1% of requests lead to errors from news database"""

my_query_3 = (
      "select day, perc from ("
      "select day, round((sum(requests)/(select count(*) from log where "
      "substring(cast(log.time as text), 0, 11) = day) * 100), 2) as "
      "perc from (select substring(cast(log.time as text), 0, 11) as day, "
      "count(*) as requests from log where status like '%404%' group by day)"
      "as log_percentage group by day order by perc desc) as final_query "
      "where perc >= 1")


def get_results(sql_query):
    try:
        # we are handling errors with try /except
        c.execute(sql_query)
    except Exception as exception:
        print("Exception\t:", exception)
    else:
        results = c.fetchall()
        return results


# method for printing query result

def print_reports(result):
    for i in range(len(result)):
        title, views = result[i]
        print("\t" + "%s ===> %d" % (title, views) + " views")


# method for printing error result

def print_error_result(result):
    for i in range(len(result)):
        date, percentage = result[i]
        print("\t" + "{} ===> {} %".format(date, percentage))


# printing results for given queries

print("1. What are the most popular three articles of all time?")
result_1 = get_results(my_query_1)
print_reports(result_1)
print("2. Who are the most popular article authors of all time?")
result_2 = get_results(my_query_2)
print_reports(result_2)
print("3. On which days did more than 1% of requests lead to errors?")
result_3 = get_results(my_query_3)
print_error_result(result_3)

# closing database connection
db.close()
