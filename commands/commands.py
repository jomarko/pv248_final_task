import ConfigParser
import subprocess
import re
import threading
from states import State


class Commands:
    def __init__(self, expressions_file):
        self.expressions = {}
        self.active_expression = None
        self.expressions_file = expressions_file
        self.lock = threading.Lock()
        self.__init_expressions()

    def f_create(self, arg):
        args = arg.split(" ", 1)
        if not self.expressions.has_key(args[0]):
            self.expressions[args[0]] = args[1]
            self.__write_expression()

        return State(State.NORMAL, "added\n")

    def f_activate(self, arg):
        if arg == '':
            self.active_expression = None
            return State(State.NORMAL, "deactivated\n")
        elif self.expressions.has_key(arg):
            self.active_expression = arg
            return State(State.NORMAL, "activated: " + arg + "\n")

        return State(State.NORMAL, "\n")

    def f_rm(self, arg):
        if arg == self.active_expression:
            self.active_expression = None
        if self.expressions.has_key(arg):
            self.expressions.pop(arg, None)
            self.__write_expression()
        return State(State.NORMAL, "removed: " + arg + "\n")

    def f_ls(self, arg):
        result = ""
        for key in self.expressions.keys():
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
                if re.match(self.expressions[self.active_expression], line):
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
        self.lock.acquire()
        config = ConfigParser.SafeConfigParser()
        config.read(self.expressions_file)

        for key in config.options("expressions"):
            self.expressions[key] = config.get("expressions", key)
        self.lock.release()

    def __write_expression(self):
        self.lock.acquire()
        cfgfile = open(self.expressions_file,'w')
        config = ConfigParser.SafeConfigParser()
        config.add_section("expressions")

        for key, value in self.expressions.iteritems():
            config.set("expressions", key, str(value))

        config.write(cfgfile)
        self.lock.release()
