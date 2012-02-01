#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
# kvigall: A customizable calender program meant for use in terminals
# Copyright (C) 2010  Niels Serup
  
# This file is part of kvigall.
#
# kvigall is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kvigall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kvigall.  If not, see <http://www.gnu.org/licenses/>.
  
##[ Name        ]## frontend.cursesfrontend
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the curses frontend
##[ Start date  ]## 2010 August 25
  
import kvigall.frontend.commandsfrontend as commands
import kvigall.various as various
import curses
import curses.ascii
import curses.textpad
import time
import locale
  
PREFERRED_ENCODING = locale.getpreferredencoding()
  
# Arrow keys
KEY_UP = 259
KEY_RIGHT = 261
KEY_DOWN = 258
KEY_LEFT = 260
KEY_MOD_UP = 65
KEY_MOD_RIGHT = 67
KEY_MOD_DOWN = 66
KEY_MOD_LEFT = 68
  
# Others
KEY_DELETE = 330
CTRL_D = ord(curses.ascii.ctrl('d'))
  
class AdvancedTextbox(curses.textpad.Textbox):
    def __init__(self, abstract_win, refresh_func):
        self.abstract_win = abstract_win
        self.refresh_func = refresh_func
        curses.textpad.Textbox.__init__(self, self.abstract_win.win)
  
    def edit(self, validate=None):
        "Edit in the widget window and collect the results."
        while 1:
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self.refresh_func()
        return self.gather()
  
  
# Modes
CMD_MODE = 1
BODY_SCROLL_MODE = 2
BODY_NAV_MODE = 3
MODE_NAMES = {
    CMD_MODE:         'command',
    BODY_SCROLL_MODE: 'scroll',
    BODY_NAV_MODE:    'navigate'
}
  
class BaseKeyInfo(object):
    def __init__(self):
        self.bindings = various.DefaultingDict()
  
    def bind(self, a, b):
        self.bindings[a].append(b)
        self.bindings[b].append(a)
  
    def get_key_info(self, key, old_key=None):
        return KeyInfo(self, key, old_key)
  
# Extra key names
KEY_EXTRA_DICT = {
    '<up>': KEY_UP,
    '<right>': KEY_RIGHT,
    '<down>': KEY_DOWN,
    '<left>': KEY_LEFT,
    '<mod-up>': KEY_MOD_UP,
    '<mod-right>': KEY_MOD_RIGHT,
    '<mod-down>': KEY_MOD_DOWN,
    '<mod-left>': KEY_MOD_LEFT,
    '<return>': curses.ascii.NL,
    '<tab>': curses.ascii.TAB,
    '<delete>': KEY_DELETE
}
  
class KeyInfo(object):
    ctrl=False
    meta=False
    key=0
    char=''
  
    def __init__(self, base, key, old_key=None):
        self.key = key
        self.base = base
        try:
            self.char = chr(key)
            if curses.ascii.isctrl(key):
                self.ctrl = True
                self.char = curses.ascii.unctrl(key)[1].lower()
        except Exception:
            pass
  
        self.meta = old_key == curses.ascii.ESC
  
    def match(self, mstr):
        bindings = self.base.bindings[mstr]
        bindings.append(mstr)
        for y in bindings:
            ok = True
            spl = y.split('-')
            if not spl[-1] in KEY_EXTRA_DICT and \
                    (self.meta and not 'M' in spl \
                    or self.ctrl and not 'C' in spl):
                continue
            for x in spl:
                if x == 'C':
                    if not self.ctrl:
                        ok = False
                        break
                    else:
                        continue
                elif x == 'M':
                    if not self.meta:
                        ok = False
                        break
                    else:
                        continue
                elif x == self.char or (x in KEY_EXTRA_DICT and KEY_EXTRA_DICT[x] == self.key):
                    break
                else:
                    ok = False
                    break
            if ok:
                return True
        # Else
        return False
  
    def __repr__(self):
        return 'Key: %d\nChar: %s\nCtrl: %s\nMeta: %s' % \
            (self.key, repr(self.char), self.ctrl and 'Yes' or 'No',
             self.meta and 'Yes' or 'No')
  
class FrontendPad(object):
    def __init__(self, frontend, width, height, x, y, x_end=-1, y_end=-1, **kwargs):
        self.frontend = frontend
        self.parent = kwargs.get('parent') or self.frontend.screen
        self.hidden = kwargs.get('hidden') or False
  
        self.width = width
        self.height = height
        self.x_coor = x
        self.y_coor = y
        self.x_end = x_end
        self.y_end = y_end
  
        self.x_scroll = 0
        self.y_scroll = 0
        self.current_text = ''
        self.use_textbox = False
        self.textbox = None
        self.old_x_coor = None
        self.old_y_coor = None
        self.clear_delay = 0
        self.update_maxes()
  
        self.create()
  
    def get_real_width(self):
        if self.width > -1:
            return self.width
        else:
            return self.x_max - self.get_real_x() + self.width
  
    def get_real_height(self):
        if self.height > -1:
            return self.height
        else:
            return self.y_max - self.get_real_y() + self.height
  
    def get_real_x(self):
        if self.x_coor > -1:
            return self.x_coor
        else:
            return self.x_max + self.x_coor
  
    def get_real_y(self):
        if self.y_coor > -1:
            return self.y_coor
        else:
            return self.y_max + self.y_coor
  
    def get_real_x_end(self):
        if self.x_end > -1:
            return self.x_end
        else:
            return self.x_max + self.x_end
  
    def get_real_y_end(self):
        if self.y_end > -1:
            return self.y_end
        else:
            return self.y_max + self.y_end
  
    def update_maxes(self):
        self.y_max, self.x_max = self.parent.getmaxyx()
  
    def create(self):
        self.win = curses.newpad(self.get_real_height(), self.get_real_width())
        self.win.idlok(1)
        self.win.scrollok(True)
        self.win.keypad(1)
  
        if self.use_textbox:
            self.add_textbox()
  
    def set_str(self, text=None, attr=0, **kwargs):
        timeout = kwargs.get('timeout')
        if text is None:
            text = self.current_text
        else:
            self.current_text = text
        self.clear()
        self.win.addstr(0, 0, text, attr)
        self.refresh()
        if timeout:
            if self.clear_delay == 0:
                self.clear_delay = timeout
                various.thread(self.clear_after, kwargs.get('atexit'))
            else:
                self.clear_delay = timeout
  
    def show_str(self, text, attr=0):
        spl = text.split('\n')
        w = max([len(x) for x in spl]) + 1
        h = len(spl)
        self.clear()
        self.resize(w, h)
        self.set_str(text, attr)
  
    def add_str(self, text, x, y, attr=0):
        self.win.addstr(y, x, text, attr)
        self.refresh()
  
    def clear_after(self, atexit=None):
        frag = 0.1
        while self.clear_delay > 0:
            time.sleep(frag)
            self.clear_delay -= frag
        self.clear_delay = 0
        self.clear()
        if atexit is not None:
            atexit()
  
    def clear(self):
        self.current_text = ''
        self.win.clear()
        self.refresh()
  
    def recreate(self):
        self.create()
        self.set_str()
  
    def resize(self, width=None, height=None):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
  
        self.recreate()
  
    def resize_x(self, width=None):
        self.resize(width, None)
  
    def resize_y(self, height=None):
        self.resize(None, height)
  
    def move(self, x=None, y=None):
        if x is not None:
            self.x_coor = x
        if y is not None:
            self.y_coor = y
  
        self.refresh()
  
    def move_x(self, x=None):
        self.move(x, None)
  
    def move_y(self, y=None):
        self.move(None, y)
  
    def temp_move(self, tmp_x=None, tmp_y=None):
        if self.old_x_coor is None:
            self.old_x_coor = self.x_coor
        if self.old_y_coor is None:
            self.old_y_coor = self.y_coor
        self.move(tmp_x, tmp_y)
  
    def temp_move_x(self, tmp_x=None):
        self.temp_move(tmp_x, None)
  
    def temp_move_y(self, tmp_y=None):
        self.temp_move(None, tmp_y)
  
    def undo_temp_move(self):
        try:
            self.move(self.old_x_coor, self.old_y_coor)
            self.old_x_coor = None
            self.old_y_coor = None
            return True
        except AttributeError:
            return False
  
    def scroll(self, x=None, y=None):
        x_scroll = self.x_scroll
        y_scroll = self.y_scroll
        x_final = self.get_real_width() - (self.x_max - self.get_real_x())
        y_final = self.get_real_height() - (self.y_max - self.get_real_y())
  
        if x is not None:
            self.x_scroll += x
            if self.x_scroll < 0:
                self.x_scroll = 0
            elif self.x_scroll > x_final:
                self.x_scroll = x_final
  
        if y is not None:
            self.y_scroll += y
            if self.y_scroll < 0:
                self.y_scroll = 0
            elif self.y_scroll > y_final:
                self.y_scroll = y_final
  
        self.refresh()
  
    def scroll_x(self, x=None):
        self.scroll(x, None)
  
    def scroll_y(self, y=None):
        self.scroll(None, y)
  
    def scroll_much(self, x=0, y=0):
        h = self.get_real_y_end() - self.get_real_y() - 2
        w = self.get_real_x_end() - self.get_real_x() - 2
        self.scroll(x * w, y * h)
  
    def scroll_x_much(self, x=0):
        self.scroll_much(x, 0)
  
    def scroll_y_much(self, y=0):
        self.scroll_much(0, y)
  
    def refresh(self):
        self.update_maxes()
        if not self.hidden:
            x_start = self.get_real_x()
            y_start = self.get_real_y()
            x_scroll = self.x_scroll
            y_scroll = self.y_scroll
            x_end = self.get_real_width() + x_start
            y_end = self.get_real_height() + y_start
            x_end = self.get_real_x_end()
            y_end = self.get_real_y_end()
            self.win.refresh(y_scroll, x_scroll,
                             y_start, x_start, y_end, x_end)
  
    def add_textbox(self):
        self.use_textbox = True
        self.textbox = AdvancedTextbox(self, self.refresh)
        return self.textbox
  
    def get_textbox(self):
        return self.textbox
  
    def remove_textbox(self):
        self.use_textbox = False
  
    def show(self):
        self.hidden = False
        self.refresh()
  
    def hide(self):
        self.hidden = True
  
class FrontendCommandLine(object):
    def __init__(self, frontend, **kwargs):
        self.frontend = frontend
        self.parent = kwargs.get('parent') or self.frontend.screen
        self.examiner = kwargs.get('examiner') or (lambda x: x)
        self.history = kwargs.get('history') or []
        self.pre_prompt = self.frontend.new_pad(3, 1, 0, -1, parent=self.parent)
        self.prompt = self.frontend.new_pad(-1, 1, 3, -1, parent=self.parent)
        self.prompt_box = self.prompt.add_textbox()
        self.msg_box = self.frontend.new_pad(80, 24, 0, 0, parent=self.parent, hidden=True)
        self.pre_msg_box = self.frontend.new_pad(-1, 1, 0, 0, parent=self.parent, hidden=True)
        self.pre_prompt.set_str('>>')
  
        self.showing_completions = False
        self.showing_message = False
        self.old_mode = None
  
    def set_examiner(self, func):
        self.examiner = func
  
    def edit(self):
        command_len = len(self.history)
        self.command_num = command_len
        # Create space for a new command
        self.history.append('')
        self.prompt.clear()
        text = self.prompt_box.edit(self.examiner)
        # Save the command
        self.history[command_len] = text
  
        return text
  
    def scroll(self, amount):
        new = self.command_num + amount
        if new >= len(self.history) or new < 0:
            return False
        self.history[self.command_num] = self.gather().rstrip()
        self.command_num += amount
        self.prompt.set_str(self.history[self.command_num])
        return True
  
    def gather(self):
        return self.prompt_box.gather()
  
    def do_command(self, ch):
        return self.prompt_box.do_command(ch)
  
    def complete_command(self):
        cmds = []
        text = self.gather().rstrip()
        for x in commands.complete_command(text):
            cmds.append(x)
        cmds_len = len(cmds)
        if cmds_len in (0, 1):
            if cmds_len == 1:
                self.prompt.set_str(cmds[0] + ' ')
            self.showing_completions = False
            self.remove_msg()
        elif cmds_len > 1 and (self.frontend.prev_key_info.match('<tab>') or self.showing_completions):
            self.showing_completions = True
            common_str = ''
            word_lengths = [len(c) for c in cmds]
            for i in range(min(word_lengths)):
                o = cmds[0][i]
                ok = True
                for x in cmds[1:]:
                    if x[i] != o:
                        ok = False
                        break
                if ok:
                    common_str += o
                else:
                    break
            self.prompt.set_str(common_str)
            word_len = max([len(c) for c in cmds]) + 2
            cmds.sort()
            height, width = self.parent.getmaxyx()
            words_per_line = width / word_len
            lines = cmds_len / words_per_line
            if cmds_len % words_per_line > 0:
                lines += 1
            words_per_line = cmds_len / lines
            if cmds_len / lines > 0:
                words_per_line += 1
  
            help_str = ''
            for i in range(cmds_len):
                help_str += cmds[i] + ' ' * (word_len - len(cmds[i]))
                if (i + 1) % words_per_line == 0:
                    help_str += '\n'
            self.show_msg(help_str)
  
    def refresh(self):
        self.pre_msg_box.refresh()
        self.msg_box.refresh()
        self.pre_prompt.refresh()
        self.prompt.refresh()
  
    def stripspaces(self, val=True):
        self.prompt_box.stripspaces = val
  
    def show_msg(self, msg, wait=None, attrs=0):
        self.showing_message = True
        spl = msg.split('\n')
        w = max([len(x) for x in spl]) + 1
        h = len(spl)
        y = self.msg_box.y_max - h
        y_middle = self.msg_box.y_max / 2
        if y < y_middle:
            y = y_middle
        self.msg_box.resize(w, h)
        self.msg_box.move_y(y)
        self.msg_box.show_str(msg, attrs)
        if wait:
            self.showing_completions = False
            curses.curs_set(0)
            self.prompt.temp_move_y(y - 2)
            self.pre_prompt.temp_move_y(y - 2)
            self.pre_msg_box.move_y(y - 1)
            self.pre_msg_box.show_str(wait, COLOR_WHITE_ON_BLACK)
            self.pre_msg_box.show()
            self.frontend.current_scroller = self.msg_box
            self.old_mode = self.frontend.mode
            self.frontend.mode = BODY_SCROLL_MODE
        else:
            self.prompt.temp_move_y(y - 1)
            self.pre_prompt.temp_move_y(y - 1)
        self.msg_box.show()
  
        self.frontend.redraw()
        self.frontend.body_win.refresh()
        self.refresh()
  
        if wait:
            while not self.examiner(self.prompt.win.getch()):
                self.refresh()
  
    def remove_msg(self):
        if not self.showing_message:
            return
        self.showing_message = False
        self.showing_completions = False
        if self.old_mode is not None:
            self.frontend.mode = self.old_mode
            self.old_mode = None
            if self.frontend.mode == CMD_MODE:
                curses.curs_set(1)
        self.msg_box.clear()
        self.msg_box.hide()
        self.pre_msg_box.clear()
        self.pre_msg_box.hide()
        self.prompt.undo_temp_move()
        self.pre_prompt.undo_temp_move()
        self.frontend.reset_current_scroller()
        self.frontend.redraw()
        self.frontend.body_win.refresh()
        self.refresh()
  
class Frontend(commands.Frontend):
    h1 = lambda self, message: message + '\n' + len(message) * '='
    h2 = lambda self, message: message + '\n' + len(message) * '-'
  
    def init(self, *settings):
        commands.Frontend.init(self)
        self.help_string += '''
  
The following modes are available:
    command: the command line in the bottom gets the focus
    scroll: the focused window is scrolled
    navigate: navigation is done directly using key combinations
  
The following key combinations can be used in general:
    Ctrl+o: switch mode
    Alt+Ctrl+o: switch mode backwards
  
Note that the Alt key may not always work. You may have to press ESC
instead of Alt.
  
The following key combinations can be used in command-mode:
    Ctrl+p or <up>: show previous command if possible
    Ctrl+n or <down>: show next command if possible
    Ctrl+b or <left>: go one character to the left
    Ctrl+f or <right>: go one character to the right
    Ctrl+a: go to the beginning of the line
    Ctrl+e: go to the end of the line
    Ctrl+d or <delete>: delete character under cursor
    Ctrl+h or <backspace>: delete character backward
    Ctrl+k: delete the entire line
  
The following key combinations can be used in scroll-mode:
    Ctrl+n or <down>: scroll down
    Ctrl+p or <up>: scroll up
    Ctrl+f or <right>: scroll right
    Ctrl+b or <left>: scroll left
  
The following key combinations can be used in navigate-mode:
    Ctrl+n or <down>: go to next eventful date
    Ctrl+p or <up>: go to previous eventful date
    Ctrl+f or <right>: go forward one day
    Ctrl+b or <left>: go backward one day\
'''
  
        self.commands_history = []
        self.prev_key = 0
        self.prev_info = None
        self.base_key_info = BaseKeyInfo()
        self.base_key_info.bind('<up>', 'C-p')
        self.base_key_info.bind('<right>', 'C-f')
        self.base_key_info.bind('<down>', 'C-n')
        self.base_key_info.bind('<left>', 'C-b')
        if 'scroll' in settings:
            self.mode = BODY_SCROLL_MODE
        elif 'navigate' in settings:
            self.mode = BODY_NAV_MODE
        else:
            self.mode = CMD_MODE
  
        self.waiting_for = None
        self.errors = []
  
    def start(self):
        commands.Frontend.start(self)
  
        curses.wrapper(self.curses_start)
  
    def read_commands_history(self):
        self.commands_history.extend(open(self.commands_history_file).read().strip().split('\n'))
  
    def write_commands_history(self):
        his = ''
        for x in self.commands_history:
            if x: his += x + '\n'
        open(self.commands_history_file, 'w').write(his)
  
    def curses_start(self, stdscr):
        self.screen = stdscr
        self.screen.idlok(1)
        self.screen.scrollok(True)
        self.screen.keypad(1)
        curses.use_default_colors()
  
        global COLOR_WHITE_ON_BLACK, COLOR_WHITE_ON_YELLOW, \
            COLOR_WHITE_ON_CYAN, COLOR_WHITE_ON_GREEN, COLOR_ERROR
  
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        COLOR_WHITE_ON_BLACK = curses.color_pair(1) | curses.A_BOLD
  
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        COLOR_WHITE_ON_YELLOW = curses.color_pair(2) | curses.A_BOLD
  
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)
        COLOR_WHITE_ON_CYAN = curses.color_pair(3) | curses.A_BOLD
  
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
        COLOR_WHITE_ON_GREEN = curses.color_pair(4) | curses.A_BOLD
  
        curses.init_pair(5, curses.COLOR_RED, -1)
        COLOR_ERROR = curses.color_pair(5)
  
        self.body_win = self.new_pad(80, 24, 0, 0, -1, -2)
        self.mode_win = self.new_pad(15, 1, -15, 0)
        self.cmd_line = self.new_command_line(history=self.commands_history, examiner=self.check_key)
        self.reset_current_scroller()
  
        if self.mode in (BODY_SCROLL_MODE, BODY_NAV_MODE):
            curses.curs_set(0)
  
        self.check_key(0)
  
        if not self.system.start_empty:
            self.show_events()
  
        self.await_command()
  
    def error(self, *msg, **kwargs):
        self.errors.append(' '.join([str(x) for x in msg]))
        cont = kwargs.get('continue')
        if cont is None:
            cont = True
        if not cont:
            self.system.exit()
  
    def reset_current_scroller(self):
        self.current_scroller = self.body_win
  
    def new_pad(self, width, height, x, y, x_end=-1, y_end=-1, **kwargs):
        return FrontendPad(self, width, height, x, y, x_end, y_end, **kwargs)
  
    def new_command_line(self, **kwargs):
        return FrontendCommandLine(self, **kwargs)
  
    def await_command(self):
        while True:
            text = self.cmd_line.edit()
            # Parse the arguments retrieved from the textbox
            result = self.process_command(text)
            if result is False:
                break
            elif isinstance(result, basestring):
                self.waiting_for = 'msg_box'
                self.cmd_line.show_msg(result, 'Press enter to quit this message. Scroll with Ctrl+N/Ctrl-V and Ctrl+P/Alt-V.')
                self.waiting_for = None
                self.cmd_line.remove_msg()
            else:
                try:
                    # Maybe it's an error
                    result = result[0]
                except Exception:
                    result = None
                if result is not None:
                    # It's an error
                    self.cmd_line.show_msg(result, None, COLOR_ERROR)
  
    def redraw(self):
        self.screen.redrawwin()
        self.screen.refresh()
  
    def refresh(self):
        self.body_win.refresh()
        self.cmd_line.refresh()
  
    def show_events(self):
        t = ''
        styled = []
        header = self.h1(self.system.get_current_date_string())
        t += header + '\n\n'
        if self.system.use_styling:
            styled.append((header, COLOR_WHITE_ON_BLACK, 0, 0))
  
        events = self.system.get_events()
        if events is None:
            msg = 'No events available.'
            if self.system.use_cache_only:
                msg += ' This is likely because you chose to only use the cache.'
            t += msg + '\n'
        elif not events:
            t += 'No events on this day.\n'
        else:
            for event in events:
                if event.type:
                    if event.subject:
                        header = (self.h2('%s: %s' % (
                                    event.type, event.subject)) + '\n').encode(PREFERRED_ENCODING)
                    else:
                        header = (self.h2('%s' % event.type) + '\n').encode(PREFERRED_ENCODING)
                else:
                    header = (self.h2('%s' % event.subject) + '\n').encode(PREFERRED_ENCODING)
                t += header
                if self.system.use_styling:
                    styled.append((header, curses.A_BOLD, 0, t.count('\n') - 2))
                inr = event.interval
                if inr:
                    t += 'Time:   %02d:%02d--%02d:%02d\n' % (
                        inr[0][0], inr[0][1], inr[1][0], inr[1][1])
                    styled.append(('Time:  ', COLOR_WHITE_ON_YELLOW, 0, t.count('\n') - 1))
                if event.author or event.projects:
                    author_str = 'Author: %s' % event.author
                    if self.system.use_styling:
                        author_str_tmp_len = len(author_str)
                    author_str = author_str.encode(PREFERRED_ENCODING)
                    if event.projects:
                        author_str += ' from %s' % ', '.join([x.encode(PREFERRED_ENCODING) for x in event.projects])
                    if self.system.use_styling:
                        styled.append(('Author:', COLOR_WHITE_ON_CYAN, 0, t.count('\n')))
                        if event.projects:
                            styled.append(('from', curses.A_BOLD, author_str_tmp_len + 1, t.count('\n')))
                    t += author_str + '\n'
                tmp_count = t.count('\n')
                t += 'Info:  ' + self.system.fill_text(' ' + (event.text.encode(PREFERRED_ENCODING) or 'None'))[7:]
                if self.system.use_styling:
                    styled.append(('Info:  ', COLOR_WHITE_ON_GREEN, 0, tmp_count))
                t += '\n\n'
        self.body_win.y_scroll = 0
        self.body_win.x_scroll = 0
        self.body_win.show_str(t)
        if self.system.use_styling:
            for x in styled:
                self.body_win.add_str(x[0], x[2], x[3], x[1])
  
    def get_key_info(self, t_key):
        return self.base_key_info.get_key_info(t_key, self.prev_key)
  
    def check_key(self, t_key):
        info = self.get_key_info(t_key)
        self.key_info = info
        def update():
            self.prev_key = t_key
            self.prev_key_info = info
  
        abort = info.match('C-g')
        switch = info.match('C-o') and 1 or info.match('C-M-o') and -1 or None
        nothing_to_do = False
        if info.match('<delete>') and self.mode == CMD_MODE:
            update()
            return CTRL_D
        if info.match('<up>'):
            if self.mode == CMD_MODE:
                self.cmd_line.scroll(-1)
            elif self.mode == BODY_SCROLL_MODE:
                self.current_scroller.scroll_y(-1)
            elif self.mode == BODY_NAV_MODE:
                self.system.goto_previous()
                self.show_events()
        elif info.match('<down>'):
            if self.mode == CMD_MODE:
                self.cmd_line.scroll(1)
            elif self.mode == BODY_SCROLL_MODE:
                self.current_scroller.scroll_y(1)
            elif self.mode == BODY_NAV_MODE:
                self.system.goto_next()
                self.show_events()
        elif info.match('C-v') and self.mode == BODY_SCROLL_MODE:
            self.current_scroller.scroll_y_much(1)
        elif info.match('M-v') and self.mode == BODY_SCROLL_MODE:
            self.current_scroller.scroll_y_much(-1)
        elif info.match('<right>') and self.mode != CMD_MODE:
            if self.mode == BODY_SCROLL_MODE:
                self.current_scroller.scroll_x(1)
            elif self.mode == BODY_NAV_MODE:
                self.system.go_forward()
                self.show_events()
        elif info.match('<left>') and self.mode != CMD_MODE:
            if self.mode == BODY_SCROLL_MODE:
                self.current_scroller.scroll_x(-1)
            elif self.mode == BODY_NAV_MODE:
                self.system.go_backward()
                self.show_events()
        elif info.match('C-k'):
            if self.mode == CMD_MODE:
                self.cmd_line.prompt.clear()
        elif info.match('<tab>'):
            if self.mode == CMD_MODE:
                self.cmd_line.complete_command()
        elif abort and self.mode == CMD_MODE:
            self.cmd_line.remove_msg()
        elif switch and not self.waiting_for:
            if self.mode == CMD_MODE:
                if switch == 1:
                    self.mode = BODY_SCROLL_MODE
                else:
                    self.mode = BODY_NAV_MODE
                curses.curs_set(0)
            elif self.mode == BODY_SCROLL_MODE:
                if switch == 1:
                    self.mode = BODY_NAV_MODE
                    curses.curs_set(0)
                else:
                    self.mode = CMD_MODE
                    curses.curs_set(1)
            elif self.mode == BODY_NAV_MODE:
                if switch == 1:
                    self.mode = CMD_MODE
                    curses.curs_set(1)
                else:
                    self.mode = BODY_SCROLL_MODE
                    curses.curs_set(0)
            slen = len(MODE_NAMES[self.mode])
            self.mode_win.clear()
            self.mode_win.width = slen
            self.mode_win.x_coor = -slen
            self.body_win.refresh()
            self.mode_win.set_str(
                MODE_NAMES[self.mode], COLOR_WHITE_ON_BLACK,
  
                timeout=2, atexit=self.refresh)
            self.cmd_line.prompt.refresh()
        else:
            nothing_to_do = True
  
        update()
        if nothing_to_do:
            if self.waiting_for == 'msg_box':
                done = info.match('<return>') or info.match('q') or abort
                return done
            else:
                return t_key
  
    def end(self):
        commands.Frontend.end(self)
        for x in self.errors:
            self.system.error(x)