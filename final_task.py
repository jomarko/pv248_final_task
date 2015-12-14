import optparse
import ConfigParser
import SocketServer
import threading
import commands


__author__ = 'jomarko'


default_options = {"server": "localhost", "port": 8888, "max": 3, "file": "expressions.ini", "re": "[a-z]*"}


def read_cfg_file(file_name, options):
    config = ConfigParser.SafeConfigParser()
    config.read(file_name)

    for key in config.options("conf"):
        if options[key] is None:
            options[key] = config.get("conf", key)


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
        action="store",
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


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True

    def __init__(self, server_address, request_handler, max_clients):
        SocketServer.TCPServer.__init__(self, server_address, request_handler)
        self.request_handler = request_handler
        self.commands_map = {}
        self.max_clients = max_clients

    def add_command(self, trigger, func):
        self.commands_map[trigger] = func

    def call_command(self, command, arg):
        if command in self.commands_map.keys():
            return self.commands_map[command](arg)
        else:
            return command + " " + arg + "\n"


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        self.server = server

    def handle(self):
        if threading.activeCount() - 1 <= self.server.max_clients:
            data = self.request.recv(1024)
            data = str.rstrip(data, "\r\n")
            parts = data.split(' ', 1)
            print parts
            if len(parts) == 2:
                result = self.server.call_command(parts[0], parts[1])
            else:
                result = self.server.call_command(parts[0], '')

            self.request.sendall(result)

        else:
            self.request.sendall("Number of max clients exceeded\n")


if __name__ == "__main__":
    options = init_options()

    real_commands = commands.Commands(options['file'])

    server = ThreadedTCPServer((options['server'], int(options['port'])), ThreadedTCPRequestHandler, options['max'])
    server.add_command("create", real_commands.f_create)
    server.add_command("activate", real_commands.f_activate)
    server.add_command("rm", real_commands.f_rm)
    server.add_command("ls", real_commands.f_ls)
    server.add_command("run", real_commands.f_run)
    server.add_command("quit", real_commands.f_quit)
    server.add_command("yes", real_commands.f_yes)
    server.add_command("no", real_commands.f_no)

    ip, port = server.server_address

    # start server
    print "Running on: %s:%s" % (ip, port)
    server.serve_forever()

    # use parser.error to report missing options or args:
#    parser.error("Option X is not set")

