#!/usr/bin/env python3
import sys
import os
import tempfile
import subprocess
import signal

# max input size (bytes) and timeout (seconds)
MAX_INP_SZ = 1 << 20    # 1 MiB
TIMEOUT_S  = 5          # adjust if you need longer

def main():
    # 1) read up to MAX_INP_SZ from stdin
    data = sys.stdin.buffer.read(MAX_INP_SZ)
    if not data:
        return 0

    # 2) dump to a temp file
    with tempfile.NamedTemporaryFile(prefix="afl_", delete=False) as f:
        f.write(data)
        tmp_path = f.name

    # 3) set an alarm so we don’t hang forever
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.alarm(TIMEOUT_S)

    # 4) invoke clang (or clang++); adjust flags as needed
    try:
        proc = subprocess.run(
            ["/usr/bin/clang", "-O3", tmp_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        # any exec failure, just exit normally
        return 0

    # 5) if clang was killed by a signal, re-raise it so AFL sees the crash
    if proc.returncode < 0:
        sig = -proc.returncode
        os.kill(os.getpid(), sig)

    # cleanup (optional)
    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    return 0

if __name__ == "__main__":
    sys.exit(main())
