# redisql

An experimental SQL client for the Redis key-value store.

## Installation

    $ git clone https://github.com/kmanley/redisql

## Getting Started

### Command line REPL

    python.exe repl.py --host <host>
    sql> insert into places (id, city, state) values (1, "Ridgefield", "CT")
    sql> insert into places (id, city, state) values (2, "New York", "NY")
    sql> insert into places (id, city, state) values (3, "Tucson", "AZ")
    sql> select * from places
    [{'city': 'Ridgefield', 'id': '1', 'state': 'CT'},
     {'city': 'Tucson', 'id': '3', 'state': 'AZ'},
     {'city': 'New York', 'id': '2', 'state': 'NY'}]
 
### Python client

    >>> from redisql.client import Client
    >>> c = Client(host, port)
    >>> c.query("insert into people (id, name, age) values (1, 'Aaron', 30)")
    >>> c.query("insert into people (id, name, age) values (2, 'Ben', 20)")
    >>> c.query("insert into people (id, name, age) values (3, 'Charlie', 40)")
    >>> c.query("insert into people (id, name, age) values (4, 'Dan', 25)")
    >>> c.query("insert into people (id, name, town, age) values (5, 'Ed', 'New York', 32)")
    >>> pprint.pprint(c.query("select * from people"))
	[{'age': '30', 'id': '1', 'name': 'Aaron'},
 	{'age': '40', 'id': '3', 'name': 'Charlie'},
 	{'age': '20', 'id': '2', 'name': 'Ben'},
 	{'age': '32', 'id': '5', 'name': 'Ed', 'town': 'New York'},
 	{'age': '25', 'id': '4', 'name': 'Dan'}]
	>>>    

## Notes
* Being implemented on Redis, the underlying "table" structure is schemaless
* "Tables" are created on the fly, each "row" can have arbitrary "columns"
* Each "row" must have an id attribute (this restriction may be lifted later)

## Roadmap

This is currently a very bare-bones implementation. Only simple inserts and
selects are supported. But so far the concept seems useful and I plan to continue
building on it. Contributions are encouraged!

The following are on the roadmap:

* support WHERE clause on SELECT
* support ORDER BY clause on SELECT
* CREATE INDEX support and transparent use of indexes
* DELETE support
* INSERT ... SELECT support
* Complex expression support 

Author
------
redisql is developed and maintained by Kevin Manley (kevin.manley@gmail.com).

It can be found here: http://github.com/kmanley/redisql

License
------
MIT License (MIT)

redisql Copyright (c) 2012 Kevin T. Manley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.





