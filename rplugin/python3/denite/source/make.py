# ============================================================================
# FILE: make.py
# AUTHOR: Johannes Ziegenbalg <Johannes dot Ziegenbalg at gmail.com>
# License: MIT license
# ============================================================================

import re
import shlex
import os, sys, stat
from os import path

from .base import Base
from denite.util import globruntime, abspath
from denite.process import Process

# TODO:
# syntax highliting
# self.vars in context
# make resume work correctly
# write filter

# Test Test Test!

class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'make'
        self.kind = 'file'
        self.vars = {
            'shell' : ['zsh', '-c'],
            'command' : "make",
            'build_setup' : "",
            'build_opts' : "",
            'build_dir' : "",

            'regex_enter' : re.compile(
                    "(\d+:)*(?P<process>\d+:).*"
                    "(?P<cd_op>Entering) directory "
                    "\'(?P<dir>.*)\'"),

            'regex_err' : re.compile(
                    "(\d+:)*(?P<process>\d+:)"
                    "(?P<file>.*)"
                    ":(?P<line>\d+):(?P<col>\d+): "
                    "(?P<tag>warning|error): "
                    "(?P<message>.*)")
        }

        self.__dir_map = {}
        self.__wrapper = '/tmp/denite-make-wrapper.sh'
        self.__last_message = { 'following_lines' : 0 }
        self.__err_numer = 0

    def on_init(self, context):
        context['__proc'] = None
        self.__create_make_wrapper()

        self.vars['build_setup'] = context['args'][0] if len(
            context['args']) > 0 else ""

        self.vars['build_opts'] = context['args'][1] if len(
            context['args']) > 1 else ""

        directory = context['args'][2] if len(
            context['args']) > 2 else context['path']
        self.vars['build_dir'] = abspath(self.vim, directory)

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None
        if path.exists(self.__wrapper):
            os.remove(self.__wrapper)

    def gather_candidates(self, context):
        # return [ { 'word' : self.vars['build_dir'] } ]
        if context['__proc']:
            return self.__async_gather_candidates(context, 0.03)

        directory = self.vars['build_dir']
        args = self.vars['shell']
        command = self.vars['build_setup'] + ' ' + self.__wrapper + ' ' + self.vars['build_opts']
        args.append(command)
        context['__proc'] = Process(args, context, directory)

        return self.__async_gather_candidates(context, 0.5)

    def __async_gather_candidates(self, context, timeout):
        outs, err = context['__proc'].communicate(timeout=timeout)
        context['is_async'] = not context['__proc'].eof()

        if context['__proc'].eof():
            context['__proc'] = None

        if err:
            return [ { 'word' : x } for x in err ]

        if not outs:
            return []

        candidates = [
            self.__convert(context, x) for x in outs
        ]
        return [ c for c in candidates if c is not None ]

    def __convert(self, context, line):
        clean_line = re.sub('(/tmp/)*denite-make-wrapper.sh', self.vars['command'], line)
        clean_line = re.sub('^\d+:', '', clean_line)

        match = self.vars['regex_err'].search( line )
        if match:
            message = match.groupdict()
            err_dir = self.__dir_map[message['process']]
            message['full_file'] = path.relpath(err_dir + "/" + message['file'], context['path'])
            message['following_lines'] = 2
            self.__err_numer += 1
            self.__last_message = message
            return {
                    'word' : '[{0}] {1}:{2}:{3}'.format(
                        message['tag'],
                        message['full_file'],
                        message['line'],
                        message['col'] ),
                    'abbr' : clean_line,
                    'action__path' : message['full_file'],
                    'action__line ': message['line'],
                    'action__col ': message['col']
            }

        if self.__last_message['following_lines'] > 0:
            self.__last_message['following_lines'] -= 1
            return {
                    'word' : '[{0}] {1}:{2}:{3}'.format(
                        self.__last_message['tag'],
                        self.__last_message['full_file'],
                        self.__last_message['line'],
                        self.__last_message['col'] ),
                    'abbr' : clean_line,
                    'action__path' : self.__last_message['full_file'],
                    'action__line ': self.__last_message['line'],
                    'action__col ': self.__last_message['col']
            }

        match = self.vars['regex_enter'].search( line )
        if match:
            message = match.groupdict()
            self.__dir_map[message['process']] = message['dir']

        # return None
        return {
            'word' : clean_line,
            'abbr' : clean_line
        }

    def __create_make_wrapper(self):
        script = [
            '#!/bin/bash',
            'PREFIX=$$:',
            'exec -a $0 ' + self.vars['command'] + ' "$@" 2>&1 | sed "s/^/$PREFIX/"'
        ]
        wrapper = open(self.__wrapper, 'w')
        wrapper.write("\n".join(script))
        wrapper.close()
        os.chmod(self.__wrapper, 0o0777)

