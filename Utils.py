# https://gist.github.com/alexbw/1187132/5de3149db6e744502c166711114bebc97af928f3

from threading import _Timer

class Timer(_Timer):
    """
    See: https://hg.python.org/cpython/file/2.7/Lib/threading.py#l1079
    """

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()

