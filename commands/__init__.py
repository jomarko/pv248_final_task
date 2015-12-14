import ConfigParser
import subprocess
expressions = {}

active_expression = None

expressions_file = None


def f_create(arg):
    args = arg.split(" ", 1)
    if not expressions.has_key(args[0]):
        expressions[args[0]] = args[1]
        write_expression()

    return "added\n"


def f_activate(arg):
    return 'activate: ' + arg


def f_rm(arg):
    if expressions.has_key(arg):
        expressions.pop(arg, None)
        write_expression()
    return "removed\n"


def f_ls(arg):
    result = ""
    for key in expressions.keys():
        result += key + "\n"

    if len(result) > 0:
        return result
    else:
        return "\n"


def f_run(arg):
    return subprocess.check_output(arg.split(" "))


def f_quit(arg):
    return 'quit: ' + arg

def init_expressions():
    config = ConfigParser.SafeConfigParser()
    config.read(expressions_file)

    for key in config.options("expressions"):
        expressions[key] = config.get("expressions", key)


def write_expression():
    cfgfile = open(expressions_file,'w')
    config = ConfigParser.SafeConfigParser()
    config.add_section("expressions")

    for key, value in expressions.iteritems():
        config.set("expressions", key, str(value))

    config.write(cfgfile)