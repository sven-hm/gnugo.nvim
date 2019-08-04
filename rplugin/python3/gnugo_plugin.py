import pygnugo
import pynvim
import os


@pynvim.plugin
class GnugoPlugin(object):

    def __init__(self, nvim):

        self.nvim = nvim
        self._gnugo = None
        self._color = None

        self._boardbuffer = None
        self._infoboardbuffer = None

        self._busy = False


    def Showboard(self):

        if self._boardbuffer is not None:
            board = self._gnugo.showboard()

            # show board
            self.nvim.command('setlocal modifiable')

            if len(self._boardbuffer) < self._gnugo._boardsize.value:
                for i in range(self._gnugo._boardsize.value + 3):
                    self._boardbuffer.append('')
            for line_number, line in enumerate(board.split('\n')):
                if line.find('BLACK') != -1 or line.find('WHITE') != -1:
                    line = line.split('  ')[0]
                self._boardbuffer[line_number] = line

            self.nvim.command('setlocal nomodifiable')


    def UpdateInfoBoard(self):

        if self._infoboardbuffer is not None:
            info_board = []

            info_board.append('')
            info_board.append('gnugo plays ' + str(self._color.other()))
            info_board.append('')
            blacks_captures = self._gnugo.captures(pygnugo.Color.BLACK)
            whites_captures = self._gnugo.captures(pygnugo.Color.WHITE)
            info_board.append(
                    'black (X) has captured {} white stones.'.format(
                        blacks_captures))
            info_board.append(
                    'white (O) has captured {} black stones.'.format(
                        whites_captures))
            info_board.append('')

            history = reversed(list(enumerate(reversed(
                self._gnugo.move_history().split('\n')))))
            info_board +=  list(
                    map(lambda h: str(h[0]) + '\t' + h[1].strip() , history))

            self._infoboardbuffer[:] = info_board


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


    @pynvim.command('GnugoLoadSgf', nargs='*', sync=True)
    def Load(self, args):

        if self._gnugo is not None:
            self.Quit()

        if len(args) == 0 or len(args) > 1:
            self.nvim.out_write('Specify filename.\n')
            return

        if not os.path.exists(args[0]):
            self.nvim.out_write('File not found.\n')
            return

        self._gnugo = pygnugo.GnuGo()

        # get game info
        _info = self._gnugo.read_sgf_info(args[0], ['PB', 'PW'])
        if len(_info['PB']) > 0 and _info['PB'][0] == 'gnugo':
            self._color = pygnugo.Color.WHITE
        elif len(_info['PW']) > 0 and _info['PW'][0] == 'gnugo':
            self._color = pygnugo.Color.BLACK
        else:
            self.nvim.out_write('Cannot read info from file..\n')
            return

        # load game
        self._gnugo.loadsgf(args[0])
        self._boardsize = self._gnugo.query_boardsize()

        self.Init()


    @pynvim.command('GnugoReload')
    def Reload(self):

        self.Load([self.nvim.eval('g:gnugonvim_current_game_file')])


    @pynvim.command('GnugoSaveSgf', nargs='*', sync=True)
    def Save(self, args):

        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

        if len(args) == 0 or len(args) > 1:
            self.nvim.out_write('Specify filename.\n')
            return

        game_info = {}
        if self._color == pygnugo.Color.BLACK:
            game_info['PW'] = 'gnugo'
        else:
            game_info['PB'] = 'gnugo'

        self._gnugo.save_with_history(args[0],
                game_information=game_info)


    @pynvim.command('GnugoNew', nargs='*', sync=True)
    def New(self, args):

        if self._gnugo is not None:
            self.Quit()

        assert(len(args) > 0 and len(args) <= 2)
        if args[0] == 'black':
            self._color = pygnugo.Color.BLACK
        elif args[0] == 'white':
            self._color = pygnugo.Color.WHITE
        else:
            self._color = pygnugo.Color.BLACK
            self.nvim.out_write('No player color found in sgf file. Gnugo plays white.\n')
            return

        if len(args) == 2:
            try:
                boardsize = pygnugo.Boardsize(args[1])
            except:
                pass
            self._gnugo = pygnugo.GnuGo(boardsize=boardsize)
            self._gnugo._boardsize.value = boardsize
        else:
            self._gnugo = pygnugo.GnuGo()

        self.Init(pygnugo.Color.BLACK
                if self._color == pygnugo.Color.WHITE
                else None)


    def Init(self, color_to_move=None):

        # open GnuGo main buffer
        self.nvim.command('setlocal splitright')
        self.nvim.command('tabnew')
        self.nvim.command('file GnuGo')
        self._boardbuffer = self.nvim.current.buffer
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
        self._infoboardbuffer = self.nvim.current.buffer
        self.nvim.command('setlocal buftype=nofile \
                                    bufhidden=hide \
                                    syntax=gnugoinfo \
                                    filetype=gnugoinfo \
                                    nolist \
                                    nonumber \
                                    wrap')


        # switch back to main split
        self.nvim.command('wincmd p')

        if type(color_to_move) == pygnugo.Color:
            self._gnugo.genmove(color_to_move)

        self.Showboard()
        self.UpdateInfoBoard()
        self.nvim.current.window.cursor = self.board2cursor('D4')


    @pynvim.command('GnugoPass')
    def Pass(self):

        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

        if self._busy:
            self.nvim.out_write('gnugo is busy\n')
        else:
            self._busy = True
            self._infoboardbuffer[0] = 'busy'
            response_position = self._gnugo.genmove(self._color.other())
            self.nvim.out_write('playing ... -> {}.\n'.format(
                response_position))
            self.Showboard()
            self.UpdateInfoBoard()
            self._busy = False


    @pynvim.command('GnugoCheat')
    def Cheat(self):

        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

        if self._busy:
            self.nvim.out_write('gnugo is busy\n')
        else:
            self._busy = True
            self._infoboardbuffer[0] = 'busy'
            self._gnugo.genmove(self._color)
            self.Showboard()
            self.UpdateInfoBoard()

            self._infoboardbuffer[0] = 'busy'
            self._gnugo.genmove(self._color.other())
            self.Showboard()
            self.UpdateInfoBoard()
            self._busy = False


    @pynvim.command('GnugoUndo')
    def Undo(self):
        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

        if self._busy:
            self.nvim.out_write('gnugo is busy\n')
        else:
            self._busy = True
            self._gnugo.undo()
            self.Showboard()
            self.UpdateInfoBoard()
            self._busy = False


    @pynvim.command('GnugoCursorUp', nargs='*', sync=True)
    def CursorUp(self, args):

        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

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
            self.nvim.out_write('No game running.\n')

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
            self.nvim.out_write('No game running.\n')

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
            self.nvim.out_write('No game running.\n')

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
            self.nvim.out_write('No game running.\n')
            return

        try:
            self.Save([self.nvim.eval('g:gnugonvim_current_game_file')])
        except:
            self.nvim.out_write('Game is lost since \
                    g:gnugonvim_current_game_file is not specified.\n')

        self._gnugo.quit()
        self.nvim.command('bdelete GnuGo')
        self.nvim.command('bdelete GnuGoInfo')
        self._boardbuffer = None
        self._infoboardbuffer = None
        self._gnugo = None


    @pynvim.command('GnugoPlay')
    def Play(self):

        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

        if self._busy:
            self.nvim.out_write('gnugo is busy\n')
        else:
            self._busy = True
            position = self.cursor2board(
                    *self.nvim.current.window.cursor)

            if position is not None:
                try:
                    self._gnugo.play(self._color, pygnugo.Vertex(position))
                except:
                    self.nvim.out_write('illegal move\n')
                    self._busy = False
                    return
                self.Showboard()
                self.UpdateInfoBoard()
                self._infoboardbuffer[0] = 'busy'
                response_position = self._gnugo.genmove(self._color.other())
                self.nvim.out_write('playing {} -> {}.\n'.format(
                    position, response_position))
                self.Showboard()
            else:
                self.nvim.out_write('Broken position.\n')

            self.UpdateInfoBoard()
            self._busy = False


    @pynvim.command('GnugoGenerateMove', nargs='*', sync=True)
    def GenerateMove(self, args):

        if self._gnugo is None:
            self.nvim.out_write('No game running.\n')

        if self._busy:
            self.nvim.out_write('gnugo is busy\n')
        else:
            self._busy = True
            assert(len(args) > 0 and len(args) <= 1)
            self._infoboardbuffer[0] = 'busy'
            if args[0] == 'black':
                self._gnugo.genmove_black()
            elif args[0] == 'white':
                self._gnugo.genmove_white()

            self.Showboard()
            self.UpdateInfoBoard()
            self._busy = False
