import optparse
import ConfigParser
import SocketServer
import threading
import commands
from commands import State as State

__author__ = 'jomarko'


default_options = {"server": "localhost", "port": 8888, "max": 3, "file": "expressions.ini", "re": []}


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


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True

    def __init__(self, server_address, request_handler, max_clients, file, preconfigured_expressions):
        SocketServer.TCPServer.__init__(self, server_address, request_handler)
        self.expressions = {}
        self.preconfigured_expressions = preconfigured_expressions
        self.max_clients = int(max_clients)
        self.file = file
        self.actual_clients = 0
        self.lock = threading.Lock()


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.commands_map = {}
        real_commands = commands.Commands(server)
        self.add_command("create", real_commands.f_create)
        self.add_command("activate", real_commands.f_activate)
        self.add_command("rm", real_commands.f_rm)
        self.add_command("ls", real_commands.f_ls)
        self.add_command("run", real_commands.f_run)
        self.add_command("quit", real_commands.f_quit)
        self.add_command("yes", real_commands.f_yes)
        self.add_command("no", real_commands.f_no)
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def add_command(self, trigger, func):
        self.commands_map[trigger] = func

    def call_command(self, command, arg):
        if command in self.commands_map.keys():
            return self.commands_map[command](arg)
        else:
            return State(State.NORMAL, command + " " + arg + "\n")

    def handle(self):
        self.server.lock.acquire()
        self.server.actual_clients += 1
        self.server.lock.release()

        old_result = State(State.NORMAL, "\n")

        if self.server.actual_clients <= self.server.max_clients:
            while True:
                data = self.request.recv(1024)
                data = str.rstrip(data, "\r\n")
                parts = data.split(' ', 1)

                if len(parts) == 2:
                    result = self.call_command(parts[0], parts[1])
                else:
                    result = self.call_command(parts[0], '')

                if old_result.state == State.WAIT:
                    if result.state == State.YES:
                        break
                    elif result.state == State.NO:
                        result.state == State.NORMAL
                        result.message = "\n"
                    else:
                        result = old_result

                old_result = result
                self.request.sendall(result.message)

        else:
            self.request.sendall("Number of max clients exceeded\n")

        self.server.lock.acquire()
        self.server.actual_clients -= 1
        self.server.lock.release()


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

    # use parser.error to report missing options or args:
#    parser.error("Option X is not set")

