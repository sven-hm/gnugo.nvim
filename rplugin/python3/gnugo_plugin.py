from gnugo import GnuGo
import pynvim


@pynvim.plugin
class GnugoPlugin(GnuGo):

    def __init__(self, nvim):

        super(GnugoPlugin, self).__init__()
        self.nvim = nvim

        self._move_history = []

        self._infoboardbuffer = None


    def Showboard(self):

        board = self.showboard()

        # show board
        self.nvim.command('setlocal modifiable')

        if len(self.nvim.current.buffer) < self._boardsize:
            for i in range(self._boardsize + 3):
                self.nvim.current.buffer.append('')
        for line_number, line in enumerate(board.split('\n')[1:]):
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

        # TODO: unload buffers
        self.quit()


    @pynvim.command('GnugoPlay')
    def Play(self):

        position = self.cursor2board(
                *self.nvim.current.window.cursor)

        if position is not None:
            self.play(position)
            self.Showboard()
            response_position = self.genmove()
            self.nvim.out_write('playing {} -> {}.\n'.format(position, response_position))
            self.Showboard()
        else:
            self.nvim.out_write('Broken position.\n')

        self.get_output()
        self._move_history.append((position, response_position))
        self.UpdateInfoBoard()
