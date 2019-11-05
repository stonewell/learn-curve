import os
import sys
import logging
import multiprocessing as mp
import wfa_runner

import signal

def handler(signum, frame):
    logging.info('keyboard interrupt')
    os._exit(1)

signal.signal(signal.SIGINT, handler)

module_path = os.path.join(os.path.dirname(__file__), "..", "..", "modules")

sys.path.append(module_path)

from data.hushen300 import hu_shen_300_stocks
sys.dont_write_bytecode = True

if __name__ == '__main__':
    mp.set_start_method('forkserver')
    argv = sys.argv[:]

    for stock_id in hu_shen_300_stocks:
        tmp_argv = argv + ['-s', stock_id]
        sys.argv = tmp_argv

        try:
            wfa_runner.wfa_runner_main()
        except(KeyboardInterrupt):
            break
        except:
            logging.exception("run for stock:%s failed", stock_id)
