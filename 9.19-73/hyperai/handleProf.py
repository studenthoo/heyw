import signal
import os
import cProfile
import pstats
import StringIO

Pr = cProfile.Profile()
Prof_enabled = False


def handler_start_prof(signum, frame):
    global Prof_enabled, Pr
    if not Prof_enabled:
        print("Start prof")
        Prof_enabled = True
        Pr.enable()


def handler_toggle_prof(signum, frame):
    global Prof_enabled, Pr
    if Prof_enabled:
        print("Stop prof")
        Prof_enabled = False
        Pr.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(Pr, stream=s).sort_stats(sortby)
        ps.print_stats(100)
        print(s.getvalue())
    else:
        print("Start prof")
        Prof_enabled = True
        Pr.enable()


def register():
    # print("==============================================")
    # print("register prof handler %s." % os.getpid())
    signal.signal(signal.SIGUSR2, handler_start_prof)
    signal.signal(signal.SIGUSR2, handler_toggle_prof)
    # print("==============================================")
    # print("register prof handler %s." % os.getpid())
    # signal.signal(signal.SIGUSR2, handler_start_prof)
    # signal.signal(signal.SIGUSR2, handler_toggle_prof)
    # print("==============================================")
    # print("register prof handler %s." % os.getpid())
    # signal.signal(signal.SIGUSR2, handler_start_prof)
    # signal.signal(signal.SIGUSR2, handler_toggle_prof)

