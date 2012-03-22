import argparse
import pprint
from client import Client
    
def main(host, port):
    c = Client(host=host, port=port)
    while True:
        text = raw_input("sql> ").strip()
        if text.lower() == "quit":
            break
        elif text:
            result = c.query(text)
            if result:
                pprint.pprint(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Redis SQL client REPL.')
    parser.add_argument('--host', dest='host', type=str, default='localhost', help='Redis host')
    parser.add_argument('--port', dest='port', type=int, default=6379, help='Redis port')
    options = parser.parse_args()
    main(options.host, options.port)
