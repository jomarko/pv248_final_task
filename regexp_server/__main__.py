import optparse
import ConfigParser

from regexp_server import ThreadedTCPRequestHandler
from regexp_server import ThreadedTCPServer

default_options = {"server": "localhost", "port": 8888, "max": 3, "file": "./data/expressions.ini", "re": []}


def read_cfg_file(file_name, options):
    config = ConfigParser.SafeConfigParser()
    config.read(file_name)

    if config.has_section("conf"):
        for key in config.options("conf"):
            if options[key] is None:
                options[key] = config.get("conf", key)

    expressions = []
    if config.has_section("re"):
        for key in config.options("re"):
            expressions.append(key + " " + config.get("re", key))

        if options["re"] is None:
            options["re"] = expressions
        else:
            options["re"] += expressions

def init_options() :
    parser = optparse.OptionParser("%prog [options]") # 1st argument is usage, %prog is replaced with sys.argv[0]
    parser.add_option(
        "-s", "--server",    # short and long option
        dest="server",       # not needed in this case, because default dest name is derived from long option
        type="string",       # "string" is default, other types: "int", "long", "choice", "float" and "complex"
        action="store",      # "store" is default, other actions: "store_true", "store_false" and "append"
        help="server address",
    )

    parser.add_option(
        "-p", "--port",
        dest="port",
        type="int",
        action="store",
        help="server port",
    )

    parser.add_option(
        "-m", "--max",
        dest="max",
        type="int",
        action="store",
        help="max number of connected clients",
    )

    parser.add_option(
        "-f", "--file",
        dest="file",
        type="string",
        action="store",
        help="configuration file with regular expressions",
    )

    parser.add_option(
        "-e", "--re",
        dest="re",
        type="string",
        action="append",
        help="regular expression",
    )

    options, args = parser.parse_args()

    real_options = vars(options)

    for arg in args:
        read_cfg_file(arg, real_options)

    for option in real_options.keys():
        if real_options[option] is None:
            real_options[option] = default_options[option]

    print real_options
    return real_options

if __name__ == "__main__":
    options = init_options()

    server = ThreadedTCPServer((options['server'], int(options['port'])),
                               ThreadedTCPRequestHandler,
                               options['max'],
                               options['file'],
                               options['re'])


    ip, port = server.server_address

    # start server
    print "Running on: %s:%s" % (ip, port)
    server.serve_forever()