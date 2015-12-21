import ConfigParser
import subprocess
import re
from states import State


class Commands:
    def __init__(self, server):
        self.active_expression = None
        self.server = server
        self.__init_expressions()
        for e in server.preconfigured_expressions:
            self.f_create(e)

    def f_create(self, arg):
        args = arg.split(" ", 1)
        if not self.server.expressions.has_key(args[0]):
            if len(args) == 2:
                self.server.expressions[args[0]] = args[1]
                self.__write_expression()
                return State(State.NORMAL, "added\n")
            else:
                return State(State.NORMAL, "missing argument\n")
        else:
            return State(State.NORMAL, "already exist\n")

    def f_activate(self, arg):
        if arg == '':
            self.active_expression = None
            return State(State.NORMAL, "deactivated\n")
        elif self.server.expressions.has_key(arg):
            self.active_expression = arg
            return State(State.NORMAL, "activated: " + arg + "\n")

        return State(State.NORMAL, "\n")

    def f_rm(self, arg):
        if arg == self.active_expression:
            self.active_expression = None
        if self.server.expressions.has_key(arg):
            self.server.expressions.pop(arg, None)
            self.__write_expression()
        return State(State.NORMAL, "removed: " + arg + "\n")

    def f_ls(self, arg):
        result = ""
        for key in self.server.expressions.keys():
            result += key + "\n"

        if len(result) > 0:
            return State(State.NORMAL, result)
        else:
            return State(State.NORMAL, "\n")

    def f_run(self, arg):
        if self.active_expression is None:
            return State(State.NORMAL, subprocess.check_output(arg.split(" ")))
        else:
            lines = str(subprocess.check_output(arg.split(" "))).split("\n")
            result = ""
            for line in lines:
                if re.match(self.server.expressions[self.active_expression], line):
                    result += line + "\n"

            if len(result) > 0:
                return State(State.NORMAL, result)
            else:
                return State(State.NORMAL, "\n")

    def f_quit(self, arg):
        return State(State.WAIT, 'Do you really want to quit? yes/no\n')

    def f_yes(self, arg):
        return State(State.YES, "yes " + arg + "\n")

    def f_no(self, arg):
        return State(State.NO, "no " + arg + "\n")

    def __init_expressions(self):
        self.server.lock.acquire()
        config = ConfigParser.SafeConfigParser()
        config.read(self.server.file)

        if config.has_section("expressions"):
            for key in config.options("expressions"):
                self.server.expressions[key] = config.get("expressions", key)
        self.server.lock.release()

    def __write_expression(self):
        self.server.lock.acquire()
        cfgfile = open(self.server.file,'w')
        config = ConfigParser.SafeConfigParser()
        config.add_section("expressions")

        for key, value in self.server.expressions.iteritems():
            config.set("expressions", key, str(value))

        config.write(cfgfile)
        self.server.lock.release()
