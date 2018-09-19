# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.

import argparse
import os.path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hyperai import get_influx_ip
# from hyperai import handleProf

# Update PATH to include the local hyperai directory
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
found_parent_dir = False
for p in sys.path:
    if os.path.abspath(p) == PARENT_DIR:
        found_parent_dir = True
        break
if not found_parent_dir:
    sys.path.insert(0, PARENT_DIR)


def main():
    # handlerProf.register()
    parser = argparse.ArgumentParser(description='hyperai server')
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=5000,
        help='Port to run app on (default 5000)'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help=('Run the application in debug mode (reloads when the source '
              'changes and gives more detailed error messages)')
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print the version number and exit'
    )

    args = vars(parser.parse_args())

    import hyperai

    if args['version']:
        print hyperai.__version__
        sys.exit()

    ip = get_influx_ip.get_status()
    if ip:
        os.environ['ip'] = ip
        
    # handleProf.register()
    print
    print r' _   _ _    _ ____  ____   ____     ____    ___  '
    print r'| |_| |\ \/ /| |- )|  __| | |- )   / /\ \  |_ _| '
    print r'|  _  | |  | | |-- |  __| | |\ \  / /__\ \  | |  '
    print r'|_| |_| |__| |_|   |____| |_| \_\/_/    \_\|___| ', hyperai.__version__
    print
    print

    import hyperai.config
    import hyperai.log
    import hyperai.webapp

    try:
        if not hyperai.webapp.scheduler.start():
            print 'ERROR: Scheduler would not start'
        else:
            hyperai.webapp.app.debug = args['debug']
            hyperai.webapp.socketio.run(hyperai.webapp.app, '0.0.0.0', args['port'])
    except KeyboardInterrupt:
        pass
    finally:
        hyperai.webapp.scheduler.stop()


if __name__ == '__main__':
    # handlerProf.register()
    main()
