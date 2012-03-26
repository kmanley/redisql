import redis
from errors import Error

class Engine(object):
    def __init__(self, **kwargs):
        self.conn = redis.StrictRedis(**kwargs)
        
    def execute(self, ast):
        retval = [getattr(self, item[0])(item[1:]) for item in ast]
        if len(retval) == 1:
            return retval[0]
            
    def iterselect(self, params):
        attnames, tablename = params
        idvalues = self.conn.smembers("%s_id" % tablename)
        for idvalue in idvalues:
            mapping = self.conn.hgetall("%s:%s" % (tablename, idvalue))
            if attnames != "*":
                mapping = {attname : mapping.get(attname) for attname in attnames}
            yield mapping

    def select(self, params):
        return list(self.iterselect(params))                
            
    def insert(self, params):
        # TODO: should keyname, attnames be case sensitive or case insensitive?
        tablename, attnames, attvalues = params
        if not len(attnames) == len(attvalues):
            raise Error("number of columns does not match number of values")
        mapping = dict(zip(attnames, attvalues))
        try:
            idvalue = mapping["id"]
        except KeyError:
            raise Error("you must specify the 'id' column and value") 
        self.conn.sadd("%s_id" % tablename, idvalue)
        self.conn.hmset("%s:%s" % (tablename, idvalue), mapping)

