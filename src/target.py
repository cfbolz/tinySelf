#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import os.path

from rply import ParsingError
from rpython.jit.codewriter.policy import JitPolicy
from rpython.rlib.compilerinfo import get_compiler_info

from tinySelf.r_io import writeln
from tinySelf.r_io import ewriteln
from tinySelf.r_io import stdin_readline

from tinySelf.version import VERSION

from tinySelf.parser import lex_and_parse

from tinySelf.vm.object_layout import Object


def run_interactive():
    o = Object()

    while True:
        line = stdin_readline(":> ")

        if len(line) == 0 or line.strip() == "exit":
            writeln()
            return 0

        if line.strip() == "p":
            writeln("o: " + str(o))
            writeln("o.slots_references: " + str(o.slots_references))
            writeln("o.map: " + str(o.map))
            # writeln("o.map.slots: " + str(o.map.slots))
            continue

        try:
            for expr in lex_and_parse(line):
                print expr.__str__()
        except ParsingError as e:
            ewriteln("Parse error.")
            if e.message:
                ewriteln(e.message)
            continue

    return 0


def run_script(path):
    print "Running script", path  # TODO: remove

    with open(path) as f:
        try:
            for expr in lex_and_parse(f.read()):
                print expr.__str__()
        except ParsingError as e:
            ewriteln("Parse error.")
            if e.message:
                ewriteln(e.message)
            return 1

    return 0


def compile_file(path):
    print "Compiling script", path  # TODO: remove

    with open(path) as f:
        try:
            for expr in lex_and_parse(f.read()):
                print expr.__str__()
        except ParsingError as e:
            ewriteln("Parse error.")
            if e.message:
                ewriteln(e.message)
            return 1

    return 0


# def run_snapshot(path):
#     print "Running snapshot", path
#     return 0


def print_help(fn):
    ewriteln("Usage:")
    ewriteln("\t%s [-h, -v] [-f FN] [-c FN] [-a FN]" % fn)
    ewriteln("")
    ewriteln("\t-a FN, --ast FN")
    ewriteln("\t\tShow AST of the `FN`.")
    ewriteln("")
    ewriteln("\t-f FN, --filename FN")
    ewriteln("\t\tRun `FN` as a tinySelf script.")
    ewriteln("")
    ewriteln("\t-c FN, --compile FN")
    ewriteln("\t\tCompile FN, output bytecode to the stdout.")
    ewriteln("")
    # ewriteln("\t-s FN, --snapshot FN")
    # ewriteln("\t\tRun memory snapshot `FN`.")
    # ewriteln("")
    ewriteln("\t-h, --help")
    ewriteln("\t\tShow this help.")
    ewriteln("")
    ewriteln("\t-v, --version")
    ewriteln("\t\tShow version and compiler information.")
    ewriteln("")
    ewriteln("\tSCRIPT_PATH")
    ewriteln("\t\tRun script `SCRIPT_PATH`.")
    ewriteln("")


def parse_arg_with_file_param(command, file):
    if not os.path.exists(file):
        ewriteln("`%s` not found!\n" % file)
        return 1

    if command in ["-a", "--ast"]:
        with open(file) as f:
            try:
                print lex_and_parse(f.read())
            except ParsingError as e:
                ewriteln("Parse error.")
                if e.message:
                    ewriteln(e.message)
                return 1
            return 0
    elif command in ["-f", "--filename"]:
        return run_script(file)
    elif command in ["-c", "--compile"]:
        return compile_file(file)
    # elif command in ["-s", "--snapshot"]:
    #     return run_script(file)

    ewriteln("Unknown command `%s`!" % command)
    return 1


def parse_args(argv):
    if len(argv) == 1:
        return run_interactive()

    elif len(argv) == 2:
        if argv[1] in ["-h", "--help"]:
            print_help(argv[0])
            return 0

        if argv[1] in ["-v", "--version"]:
            print "tSelf", VERSION
            print get_compiler_info()
            return 0

        elif argv[1].startswith("-"):
            ewriteln(
                "%s probably requires a parameter. See --help for details!" % argv[1]
            )
            return 1

        elif not os.path.exists(argv[1]):
            ewriteln("Unrecognized option `%s`!" % argv[1])
            return 1

        else:
            return run_script(argv[1])

    elif len(argv) == 3:
        return parse_arg_with_file_param(argv[1], argv[2])

    else:
        ewriteln("Unknown arguments `%s`!" % str(argv[1:]))
        return 1

    return 0


def main(argv):
    return parse_args(argv)


def target(driver, args):
    return main, None


def jitpolicy(driver):
    return JitPolicy()


def untranslated_main():
    """
    Runs main, exiting with the appropriate exit status afterwards.
    """
    import sys
    sys.exit(main(sys.argv))


if __name__ == '__main__':
    untranslated_main()
