import pygnugo
import pynvim


@pynvim.plugin
class GnugoPlugin(object):

    def __init__(self, nvim):

        self.nvim = nvim
        self._move_history = []
        self._infoboardbuffer = None
        self._gnugo = None


    def Showboard(self):

        board = self._gnugo.showboard()

        # show board
        self.nvim.command('setlocal modifiable')

        if len(self.nvim.current.buffer) < self._gnugo._boardsize.value:
            for i in range(self._gnugo._boardsize.value + 3):
                self.nvim.current.buffer.append('')
        for line_number, line in enumerate(board.split('\n')):
            if line.find('BLACK') != -1 or line.find('WHITE') != -1:
                line = line.split('  ')[0]
            self.nvim.current.buffer[line_number] = line

        self.nvim.command('setlocal nomodifiable')


    def UpdateInfoBoard(self):

        # store cursor position
        _last_position = self.nvim.current.window.cursor
        # show game info
        self.nvim.command('buffer GnuGoInfo')
        self.nvim.command('setlocal modifiable')

        head_str = '\tBLACK\tWHITE'
        if len(self.nvim.buffers[self._infoboardbuffer]) == 0:
            self.nvim.current.buffer.append(head_str)
        else:
            self.nvim.current.buffer[0] = head_str

        for ii, move in enumerate(self._move_history):
            ii += 1
            mv_str = str(ii) + ':\t' + move[0] + '\t\t' + move[1]
            if ii >= len(self.nvim.buffers[self._infoboardbuffer]):
                #self.nvim.buffers[self._infoboardbuffer].append(mv_str)
                self.nvim.current.buffer.append(mv_str)
            else:
                #self.nvim.buffers[self._infoboardbuffer][ii] = mv_str
                self.nvim.current.buffer[ii] = mv_str

        self.nvim.command('setlocal nomodifiable')
        self.nvim.command('buffer GnuGo')

        # restort cursor position
        self.nvim.current.window.cursor = _last_position


    def cursor2board(self, row, column):

        row = self._gnugo._boardsize.value - row + 2
        if row < 1 or row > self._gnugo._boardsize.value:
            return None
        if (column - 3) % 2 == 1:
            return None
        column_index = int((column-3) / 2)
        if column_index < 0 or column_index > self._gnugo._boardsize.value - 1:
            return None
        column = "ABCDEFGHJKLMNOPQRST"[column_index]

        return str(column) + str(row)


    def board2cursor(self, pos):

        try:
            row = int(pos[1:])
            column = pos[0]
        except:
            return None
        row = self._gnugo._boardsize.value - row + 2
        column_index = "ABCDEFGHJKLMNOPQRST".find(column)
        column = column_index * 2 + 3
        return (row, column)


    @pynvim.command('GnugoNew', nargs='*', sync=True)
    def New(self, args):

        assert(len(args) > 0 and len(args) <= 2)
        if args[0] == 'black':
            self._color = pygnugo.Color.BLACK
        elif args[0] == 'white':
            self._color = pygnugo.Color.WHITE
        else:
            self.nvim.out_write('Color should be black or white.\n')
            return

        if len(args) == 2:
            try:
                boardsize = pygnugo.Boardsize(args[1])
            except:
                pass
            self._gnugo = pygnugo.GnuGo(color=args[0], boardsize=boardsize)
            self._gnugo._boardsize.value = boardsize
        else:
            self._gnugo = pygnugo.GnuGo(color=args[0])

        if self._color == pygnugo.Color.WHITE:
            self._gnugo.genmove()

        # open GnuGo main buffer
        self.nvim.command('setlocal splitright')
        self.nvim.command('tabnew')
        self.nvim.command('file GnuGo')
        self.nvim.command('filetype plugin on')
        self.nvim.command('setlocal buftype=nofile \
                                    nomodifiable \
                                    bufhidden=hide \
                                    syntax=gnugo \
                                    filetype=gnugo \
                                    nolist \
                                    nonumber \
                                    wrap')

        # open GnuGoInfo buffer
        self.nvim.command('vnew')
        self.nvim.command('file GnuGoInfo')
        self.nvim.command('setlocal buftype=nofile \
                                    nomodifiable \
                                    bufhidden=hide \
                                    nolist \
                                    nonumber \
                                    wrap')

        self._infoboardbuffer = self.nvim.current.buffer.number

        # switch back to main split
        self.nvim.command('wincmd p')

        self.Showboard()
        self.nvim.current.window.cursor = self.board2cursor('D4')


    @pynvim.command('GnugoContinue')
    def Continue(self):

        if self._gnugo is None:
            self.nvim.out_write('No game running.')
        self.nvim.out_write('Not implemented.')


    @pynvim.command('GnugoCheat')
    def Cheat(self):

        if self._gnugo is None:
            self.nvim.out_write('No game running.')
        self.nvim.out_write('Not implemented.')


    @pynvim.command('GnugoListMoves')
    def ListMoves(self):

        # TODO
        # open split window and list last moves
        if self._gnugo is None:
            self.nvim.out_write('No game running.')
        self.nvim.out_write('Not implemented.')


    @pynvim.command('GnugoCursorUp', nargs='*', sync=True)
    def CursorUp(self, args):

        if self._gnugo is None:
            self.nvim.out_write('No game running.')

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

        if self._gnugo is None:
            self.nvim.out_write('No game running.')

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

        if self._gnugo is None:
            self.nvim.out_write('No game running.')

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

        if self._gnugo is None:
            self.nvim.out_write('No game running.')

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

        if self._gnugo is None:
            self.nvim.out_write('No game running.')

        # TODO: unload buffers
        self._gnugo.quit()


    @pynvim.command('GnugoPlay')
    def Play(self):

        if self._gnugo is None:
            self.nvim.out_write('No game running.')

        position = self.cursor2board(
                *self.nvim.current.window.cursor)

        if position is not None:
            self._gnugo.play(self._color, pygnugo.Vertex(position))
            self.Showboard()
            response_position = self._gnugo.genmove(self._color.other())
            self.nvim.out_write('playing {} -> {}.\n'.format(position, response_position))
            self.Showboard()
        else:
            self.nvim.out_write('Broken position.\n')

        self._move_history.append((position, response_position))
        self.UpdateInfoBoard()
