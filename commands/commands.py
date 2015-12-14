import ConfigParser
import subprocess


class Commands:

    def __init__(self, expressions_file):
        self.expressions = {}
        self.active_expression = None
        self.expressions_file = expressions_file
        self.init_expressions()

    def f_create(self, arg):
        args = arg.split(" ", 1)
        if not self.expressions.has_key(args[0]):
            self.expressions[args[0]] = args[1]
            self.write_expression()

        return "added\n"


    def f_activate(self, arg):
        if arg == '':
            self.active_expression = None
            return "deactivated\n"
        elif self.expressions.has_key(arg):
            active_expression = arg
            return "activated" + arg + "\n"

        return "\n"


    def f_rm(self, arg):
        if self.expressions.has_key(arg):
            self.expressions.pop(arg, None)
            self.write_expression()
        return "removed\n"


    def f_ls(self, arg):
        result = ""
        for key in self.expressions.keys():
            result += key + "\n"

        if len(result) > 0:
            return result
        else:
            return "\n"


    def f_run(self, arg):
        return subprocess.check_output(arg.split(" "))


    def f_quit(self, arg):
        return 'quit: yes/no?\n'


    def f_yes(self, arg):
        pass


    def f_no(self, arg):
        pass


    def init_expressions(self):
        print self.expressions_file
        config = ConfigParser.SafeConfigParser()
        config.read(self.expressions_file)

        for key in config.options("expressions"):
            self.expressions[key] = config.get("expressions", key)


    def write_expression(self):
        cfgfile = open(self.expressions_file,'w')
        config = ConfigParser.SafeConfigParser()
        config.add_section("expressions")

        for key, value in self.expressions.iteritems():
            config.set("expressions", key, str(value))

        config.write(cfgfile)
