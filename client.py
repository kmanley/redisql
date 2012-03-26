from engine import Engine
from sqlparser import SqlLexer, SqlParser

class Client(object):
    def __init__(self, host="localhost", port=6379, verbose=False):
        self.engine = Engine(host=host, port=port, verbose=verbose)
        self.lexer = SqlLexer().build()
        self.parser = SqlParser().build()
        
    def query(self, sql):
        ast = self.parser.parse(sql, lexer=self.lexer)
        if ast:
            result = self.engine.execute(ast)
            return result

def unittest():
    import pprint
    c = Client("192.168.56.101")
    c.query("insert into people (id, name, age) values (1, 'Aaron', 30)")
    c.query("insert into people (id, name, age) values (2, 'Ben', 20)")
    c.query("insert into people (id, name, age) values (3, 'Charlie', 40)")
    c.query("insert into people (id, name, age) values (4, 'Dan', 25)")
    c.query("insert into people (id, name, town, age) values (5, 'Ed', 'New York', 32)")
    pprint.pprint(c.query("select * from people"))
    print "-" * 40
    pprint.pprint(c.query("select name, age from people"))
    print "-" * 40
    pprint.pprint(c.query("select id, name, town from people"))

if __name__ == "__main__":
    unittest()
