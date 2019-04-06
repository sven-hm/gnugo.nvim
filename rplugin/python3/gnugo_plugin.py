#!/usr/bin/python3

import pynvim

from subprocess import Popen, PIPE, STDOUT
from queue import Queue
from threading import Thread

import time

class GnuGo(object):

    def __init__(self):

        self._gnugo = None

    def start(self, color='black', boardsize=19):

        if self._gnugo is not None:
            self.quit()

        self._color = color
        self._boardsize = boardsize
        self._outputQ = Queue()
        cmd = ['gnugo',
                '--mode', 'gtp',
                #'-l', '/home/sven/.config/nvim/rplugin/python3/test.sgf',
                '--boardsize', '{0}'.format(self._boardsize)]
        self._gnugo = Popen(cmd,
                stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self._readoutputthread = Thread(
                target=self._fillQ,
                args=[self._gnugo.stdout, self._outputQ])
        self._readoutputthread.daemon = True
        self._readoutputthread.start()

    def load(self, filename):
        # TODO
        pass

    def quit(self):
        if self._gnugo is not None:
            self.send('quit')

    def _fillQ(self, output, Q):
        for line in iter(output.readline, ''):
            Q.put(line)
        output.close()

    def send(self, cmd):
        if self._gnugo is None:
            self.nvim.out_write('Gnugo is not running.\n')
            return

        self._gnugo.stdin.write('{0}\n'.format(cmd).encode('utf-8'))
        self._gnugo.stdin.flush()

    def get_output(self):
        output = ''
        if self._gnugo is None:
            self.nvim.out_write('Gnugo is not running.\n')
            return ''

        while not self._outputQ.empty():
            output += self._outputQ.get().decode()
        return output

    def play(self, position):
        self.send('play ' + self._color + ' ' + position)
        while True:
            time.sleep(0.1)
            if self.get_output().find('=') != -1:
                break

    def genmove(self):
        if self._gnugo is None:
            self.nvim.out_write('Gnugo is not running.\n')
            return
        if self._color == 'black':
            self.send('genmove white')
        else:
            self.send('genmove black')
        while True:
            time.sleep(0.5)
            output = self.get_output()
            if output.find('=') != -1:
                return output.split('=')[1].strip()

    def showboard(self):
        self.get_output()
        self.send('showboard')
        time.sleep(0.1)
        while True:
            time.sleep(0.1)
            board = self.get_output()
            if board.find('=') != -1:
                return board

@pynvim.plugin
class GnugoPlugin(GnuGo):

    def __init__(self, nvim):
        super(GnugoPlugin, self).__init__()
        self.nvim = nvim

    def Showboard(self):

        board = self.showboard()

        self.nvim.command('setlocal modifiable')

        if len(self.nvim.current.buffer) < self._boardsize:
            for i in range(self._boardsize + 3):
                self.nvim.current.buffer.append('')
        for line_number, line in enumerate(board.split('\n')[1:]):
            if line.find('BLACK') != -1 or line.find('WHITE') != -1:
                line = line.split('  ')[0]
            self.nvim.current.buffer[line_number] = line

        self.nvim.command('setlocal nomodifiable')

    def showcursor(self, position):
        self.nvim.command('setlocal modifiable')
        self.nvim.current.buffer[self._boardsize - 2] += '     Cursor ' + str(position)
        self.nvim.command('setlocal nomodifiable')

    def cursor2board(self, row, column):
        row = self._boardsize - row + 2
        if row < 1 or row > self._boardsize:
            return None
        if (column - 3) % 2 == 1:
            return None
        column_index = int((column-3) / 2)
        if column_index < 0 or column_index > self._boardsize - 1:
            return None
        column = "ABCDEFGHJKLMNOPQRST"[column_index]
        return str(column) + str(row)

    def board2cursor(self, pos):
        try:
            row = int(pos[1:])
            column = pos[0]
        except:
            return None
        row = self._boardsize - row + 2
        column_index = "ABCDEFGHJKLMNOPQRST".find(column)
        column = column_index * 2 + 3
        return (row, column)

    @pynvim.command('GnugoNew', nargs='*', sync=True)
    def New(self, args):

        assert(len(args) > 0 and len(args) <= 2)
        assert(args[0] == 'black' or args[0] == 'white')
        if len(args) == 2:
            try:
                boardsize = int(args[1])
            except:
                pass
            self.start(color=args[0], boardsize=boardsize)
            self._boardsize = boardsize
        else:
            self.start(color=args[0])

        if self._color == 'white':
            self.genmove()

        self.nvim.command('setlocal splitright')
        self.nvim.command('new')
        self.nvim.command('filetype plugin on')
        self.nvim.command('setlocal buftype=nofile \
                                    bufhidden=hide \
                                    syntax=gnugo \
                                    filetype=gnugo \
                                    nolist \
                                    nonumber \
                                    wrap')
        self.Showboard()

        self.nvim.current.window.cursor = self.board2cursor('D4')

    @pynvim.command('GnugoContinue')
    def Continue(self):
        pass

    @pynvim.command('GnugoCheat')
    def Cheat(self):
        pass

    @pynvim.command('GnugoListMoves')
    def ListMoves(self):
        # TODO
        # open split window and list last moves
        pass

    @pynvim.command('GnugoCursorUp', nargs='*', sync=True)
    def CursorUp(self, args):

        if len(args) == 1:
            shift = int(args[0])
        else:
            shift = 1

        if self.cursor2board(
                self.nvim.current.window.cursor[0] - shift,
                self.nvim.current.window.cursor[1]) is not None:
            self.nvim.current.window.cursor = (
                    self.nvim.current.window.cursor[0] - shift,
                    self.nvim.current.window.cursor[1])

        self.nvim.out_write('cursor: {}\n'.format(
            self.cursor2board(*self.nvim.current.window.cursor)))

    @pynvim.command('GnugoCursorDown', nargs='*', sync=True)
    def CursorDown(self, args):

        if len(args) == 1:
            shift = int(args[0])
        else:
            shift = 1

        if self.cursor2board(
                self.nvim.current.window.cursor[0] + shift,
                self.nvim.current.window.cursor[1]) is not None:
            self.nvim.current.window.cursor = (
                    self.nvim.current.window.cursor[0] + shift,
                    self.nvim.current.window.cursor[1])

        self.nvim.out_write('cursor: {}\n'.format(
            self.cursor2board(*self.nvim.current.window.cursor)))

    @pynvim.command('GnugoCursorLeft', nargs='*', sync=True)
    def CursorLeft(self, args):

        if len(args) == 1:
            shift = 2 * int(args[0])
        else:
            shift = 2

        if self.cursor2board(
                self.nvim.current.window.cursor[0],
                self.nvim.current.window.cursor[1] - shift) is not None:
            self.nvim.current.window.cursor = (
                    self.nvim.current.window.cursor[0],
                    self.nvim.current.window.cursor[1] - shift)

        self.nvim.out_write('cursor: {}\n'.format(
            self.cursor2board(*self.nvim.current.window.cursor)))

    @pynvim.command('GnugoCursorRight', nargs='*', sync=True)
    def CursorRight(self, args):

        if len(args) == 1:
            shift = 2 * int(args[0])
        else:
            shift = 2

        if self.cursor2board(
                self.nvim.current.window.cursor[0],
                self.nvim.current.window.cursor[1] + shift) is not None:
            self.nvim.current.window.cursor = (
                    self.nvim.current.window.cursor[0],
                    self.nvim.current.window.cursor[1] + shift)

        self.nvim.out_write('cursor: {}\n'.format(
            self.cursor2board(*self.nvim.current.window.cursor)))

    @pynvim.command('GnugoQuit')
    def Quit(self):
        self.quit()

    @pynvim.command('GnugoPlay')
    def Play(self):

        position = self.cursor2board(
                *self.nvim.current.window.cursor)

        if position is not None:
            self.play(position)
            time.sleep(0.1)
            self.Showboard()
            response_position = self.genmove()
            self.nvim.out_write('playing {} -> {}.\n'.format(position, response_position))
            self.Showboard()
        else:
            self.nvim.out_write('Broken position.\n')

        self.get_output()
        self.Showboard()
