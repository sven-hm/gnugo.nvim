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

        # TODO: end all processes
        if self._gnugo is not None:
            self.send('quit')


    def _fillQ(self, output, Q):

        for line in iter(output.readline, ''):
            Q.put(line)
        output.close()


    def send(self, cmd):

        if self._gnugo is None:
            return

        self._gnugo.stdin.write('{0}\n'.format(cmd).encode('utf-8'))
        self._gnugo.stdin.flush()


    def get_output(self):

        output = ''
        if self._gnugo is None:
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
            return
        if self._color == 'black':
            self.send('genmove white')
        else:
            self.send('genmove black')
        while True:
            time.sleep(0.1)
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
