# TODO: consider storing multiple versions of each entity
import pprint
import redis
from errors import Error
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class Engine(object):
    def __init__(self, **kwargs):
        try:
            self.verbose = kwargs.pop("verbose")
        except KeyError:
            pass
        self.conn = redis.StrictRedis(**kwargs)        
        
    def redis(self, func, *args, **kwargs):
        retval = func(*args, **kwargs)
        if self.verbose:
            log.debug("REDIS: %s(%s, %s) -> %s" % (func.__name__, repr(args)[1:-1], kwargs or "", repr(retval)))
        return retval
        
    def execute(self, ast):
        if self.verbose:
            log.debug("AST: %s" % pprint.pformat(ast))
        retval = [getattr(self, item[0])(item[1:]) for item in ast]
        if len(retval) == 1:
            return retval[0]
            
    def iterselect(self, params):
        conn = self.conn
        attnames, tablename, whereclause, orderbyatt = params
        idvalues = self.redis(conn.smembers, "%s_id" % tablename)
        if attnames == "*":
            for idvalue in idvalues:
                mapping = self.redis(conn.hgetall, "%s:%s" % (tablename, idvalue))
                yield mapping
        else:
            for idvalue in idvalues:
                data = self.redis(conn.hmget, "%s:%s" % (tablename, idvalue), attnames)
                yield dict(zip(attnames, data))

    def select(self, params):
        attnames, tablename, whereclause, orderbyatt = params
        rowset = list(self.iterselect(params))
        if orderbyatt:
            rowset.sort(lambda lhs, rhs : cmp(lhs.get(orderbyatt), rhs.get(orderbyatt)))  
        return rowset              
            
    def insert(self, params):
        tablename, attnames, attvalues = params
        #tablename = tablename.lower()
        #attnames = [attname.lower() for attname in attnames]
        if not len(attnames) == len(attvalues):
            raise Error("number of columns does not match number of values")
        mapping = dict(zip(attnames, attvalues))
        try:
            idvalue = mapping["id"]
        except KeyError:
            raise Error("you must specify the 'id' column and value") 
        self.conn.sadd("%s_id" % tablename, idvalue)
        self.conn.hmset("%s:%s" % (tablename, idvalue), mapping)

