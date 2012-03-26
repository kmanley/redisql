"""
See links for example yacc SQL grammars:
http://yaxx.googlecode.com/svn/trunk/sql/sql2.y

# TODO: support select fname + ' ' + lname from people
see grammar above

"""
from ply import lex, yacc

class SqlLexer(object):

    reserved = {
       'insert' : 'INSERT', 
       'into'   : 'INTO',
       'select' : 'SELECT',
       'from'   : 'FROM',
       'where'  : 'WHERE',
       'order'  : 'ORDER',
       'by'     : 'BY',
       'values' : 'VALUES',
       'and'    : 'AND',
       'or'     : 'OR',
       'not'    : 'NOT',
    } 
    
    tokens = ['NUMBER',
              'ID', 
              'STRING',
              'COMMA',      'SEMI',
              'PLUS',       'MINUS',
              'TIMES',      'DIVIDE',
              'LPAREN',     'RPAREN',
              'GT',         'GE',
              'LT',         'LE',
              'EQ',         'NE', 
              ] + list(reserved.values())
    
    def t_NUMBER(self, t):
        # TODO: see http://docs.python.org/reference/lexical_analysis.html
        # for what Python accepts, then use eval
        r'\d+'
        t.value = int(t.value)    
        return t
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = SqlLexer.reserved.get(t.value,'ID')    # Check for reserved words
        # redis is case sensitive in hash keys but we want the sql to be case insensitive,
        # so we lowercase identifiers 
        t.value = t.value.lower()
        return t
    
    def t_STRING(self, t):
        # TODO: unicode...
        # Note: this regex is from pyparsing, 
        # see http://stackoverflow.com/questions/2143235/how-to-write-a-regular-expression-to-match-a-string-literal-where-the-escape-is
        # TODO: may be better to refer to http://docs.python.org/reference/lexical_analysis.html 
        '(?:"(?:[^"\\n\\r\\\\]|(?:"")|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*")|(?:\'(?:[^\'\\n\\r\\\\]|(?:\'\')|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*\')'
        t.value = eval(t.value) 
        #t.value[1:-1]
        return t
        
    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    t_ignore  = ' \t'
    
    #literals = ['+', '-', '*', '/', '>', '>=', '<', '<=', '=', '!=']
    # Regular expression rules for simple tokens
    t_COMMA   = r'\,'
    t_SEMI    = r';'
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_GT      = r'>'
    t_GE      = r'>='
    t_LT      = r'<'
    t_LE      = r'<='
    t_EQ      = r'='
    t_NE      = r'!='
    #t_NE      = r'<>'
    
    def t_error(self, t):
        raise TypeError("Unknown text '%s'" % (t.value,))

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

    def test(self):
        while True:
            text = raw_input("sql> ").strip()
            if text.lower() == "quit":
                break
            self.lexer.input(text)
            while True:
                tok = self.lexer.token()
                if not tok: 
                    break
                print tok
        
# TODO: consider using a more formal AST representation        
#class Node(object):
#    def __init__(self, children=None, leaf=None):
#        if children:
#            self.children = children
#        else:
#            self.children = [ ]
#        self.leaf = leaf
        
class SqlParser(object):
    
    tokens = SqlLexer.tokens
    
    #def p_empty(self, p):
    #    'empty :'
    #    pass    
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),
        ('left', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        )
    
    def p_statement_list(self, p):
        """
        statement_list : statement
                       | statement_list statement
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
            
    def p_statement(self, p):
        """
        statement : insert_statement
                  | select_statement
        """
        p[0] = p[1]
    
    def p_insert_statement(self, p):
        # TODO: support extension: insert into X (a,b,c) VALUES (a1,b1,c1), (a2,b2,c2), ...
        """
        insert_statement : INSERT ID LPAREN id_list RPAREN VALUES LPAREN expr_list RPAREN
                         | INSERT INTO ID LPAREN id_list RPAREN VALUES LPAREN expr_list RPAREN 
        """
        if p[2].lower() == "into":
            p[0] = ('insert', p[3], p[5], p[9])
        else:
            p[0] = ('insert', p[2], p[4], p[8])

    def p_select_statement(self, p):
        """
        select_statement : SELECT select_columns FROM ID opt_where_clause opt_orderby_clause
        """
        p[0] = ('select', p[2], p[4], p[5], p[6])
        
    def p_select_columns(self, p):
        """
        select_columns : TIMES
                       | id_list
        """
        p[0] = p[1]
        
    def p_opt_where_clause(self, p):
        """
        opt_where_clause : WHERE search_condition
                         |
        """
        if len(p) == 1:
            p[0] = None
        else:
            p[0] = p[2]
            
    def p_search_condition(self, p):
        """
        search_condition : search_condition OR search_condition
                         | search_condition AND search_condition
                         | NOT search_condition
                         | LPAREN search_condition RPAREN
                         | predicate
        """
        lenp = len(p)
        if lenp == 4:
            if p[1] == '(':
                p[0] = p[2]
            else:
                p[0] = (p[2], p[1], p[3])
        elif lenp == 3:
            p[0] = (p[1], p[2])
        else:
            p[0] = p[1]
            
    # TODO: there are other predicates...see sql2.y            
    def p_predicate(self, p):
        """
        predicate : comparison_predicate
        """
        p[0] = p[1]
        
    def p_comparison_predicate(self, p):
        """
        comparison_predicate : scalar_exp EQ scalar_exp
                             | scalar_exp NE scalar_exp
                             | scalar_exp LT scalar_exp
                             | scalar_exp LE scalar_exp
                             | scalar_exp GT scalar_exp
                             | scalar_exp GE scalar_exp
        """
        p[0] = (p[2], p[1], p[3])
        
    # TODO: unify this with old expr rules
    def p_scalar_exp(self, p):
        """
        scalar_exp : scalar_exp PLUS scalar_exp
                   | scalar_exp MINUS scalar_exp
                   | scalar_exp TIMES scalar_exp
                   | scalar_exp DIVIDE scalar_exp
                   | atom
                   | LPAREN scalar_exp RPAREN
        """
        lenp = len(p)
        if lenp == 4:
            if p[1] == "(":
                p[0] = p[2]
            else:
                p[0] = (p[2], p[1], p[3])
        elif lenp == 2:
            p[0] = p[1]
        else:
            raise AssertionError()
        
    def p_atom(self, p):
        """
        atom : NUMBER
             | ID
             | STRING
        """
        p[0] = p[1]
            
    # TODO: more advanced order by including multiple columns, asc/desc            
    def p_opt_orderby_clause(self, p):
        """
        opt_orderby_clause : ORDER BY ID
                           |
        """
        if len(p) == 1:
            p[0] = None
        else:
            p[0] = p[3]
            
    #def p_conditional_expr(self, p):
    #    """
    #    conditional_expr : relational_expr
    #                     | conditional_expr AND conditional_expr
    #                     | conditional_expr OR conditional_expr
    #    """
    #    if len(p) == 2:
    #        p[0] = [p[1]]
    #    else:
    #        p[0] = (p[2], p[1], p[3])
            
    #def p_relational_expr(self, p):
    #    """
    #    relational_expr : expr LT expr
    #                    | expr LE expr
    #                    | expr GT expr
    #                    | expr GE expr
    #                    | expr EQ expr
    #    """
    #    p[0] = (p[2], p[1], p[3])
        
    def p_id_list(self, p):
        """
        id_list : ID
                | id_list COMMA ID
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_expr_list(self, p):
        """
        expr_list : expr
                  | expr_list COMMA expr
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_expr(self, p):
        """
        expr : expr PLUS term
             | expr MINUS term
             | term
             | ID
             | STRING
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ('binop', p[2], p[1], p[3])
            
    def p_term(self, p):
        """
        term : term TIMES factor
             | term DIVIDE factor
             | factor
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ('binop', p[2], p[1], p[3])

    def p_factor(self, p):
        """
        factor : NUMBER
               | LPAREN expr RPAREN
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2] 
    
    def p_error(self, p):
        print "Syntax error in input" # TODO: at line %d, pos %d!" % (p.lineno)
    
    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser

    def test(self):
        lexer = SqlLexer().build()
        while True:
            text = raw_input("sql> ").strip()
            if text.lower() == "quit":
                break
            if text:
                result = self.parser.parse(text, lexer=lexer)
                print "parse result -> %s" % result
        

def unittest_lexer():
    l = SqlLexer()
    l.build()
    l.test()
        
def unittest_parser():
    p = SqlParser()
    p.build()
    p.test()
    
if __name__ == "__main__":    
    #unittest_lexer()
    unittest_parser()
    
                