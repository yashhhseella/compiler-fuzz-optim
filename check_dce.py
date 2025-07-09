#!/usr/bin/env python3
import os, sys, subprocess, tempfile, shutil, re, signal

src = sys.argv[1]
tmp = tempfile.mkdtemp(prefix="dce")
bc0, bcD = [os.path.join(tmp, f) for f in ("o0.bc", "dce.bc")]
ir0, irD = [p.replace(".bc", ".ll") for p in (bc0, bcD)]

try:
    # 1) Emit O0 LLVM bitcode
    subprocess.run(
        ["clang","-O0","-emit-llvm","-c",src,"-o",bc0],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )
    # 2) Run just the ADCE pass
    subprocess.run(
        ["opt","-S","-adce",bc0,"-o",bcD],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )
    # 3) Disassemble both versions
    subprocess.run(["llvm-dis",bc0,"-o",ir0], check=True)
    subprocess.run(["llvm-dis",bcD,"-o",irD], check=True)

    # 4) Check for removed lines
    before = open(ir0).readlines()
    after  = open(irD).readlines()
    removed = len(before) - len(after)

    if removed > 0:
        # **interesting** → crash via SIGABRT
        os.abort()
    else:
        # **not interesting** → normal exit
        sys.exit(0)

except subprocess.CalledProcessError:
    # malformed input → treat as non-interesting
    sys.exit(0)

finally:
    shutil.rmtree(tmp, ignore_errors=True)