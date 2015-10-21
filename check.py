#!/usr/bin/python

import argparse
import subprocess
import sys

arg_map = {
   "src/pyblk" : [
      "--reports=no",
      "--disable=I",
      "--disable=bad-continuation",
      "--disable=duplicate-code",
      "--msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}'"
   ],
   "tests" : [
      "--reports=no",
      "--disable=I",
      "--disable=bad-continuation",
      "--disable=duplicate-code",
      "--disable=no-self-use",
      "--msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}'"
   ]
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
       "package",
       choices=arg_map.keys(),
       help="designates the package to test"
    )
    args = parser.parse_args()
    cmd = ["pylint", args.package] + arg_map[args.package]
    return subprocess.call(cmd, stdout=sys.stdout)


if __name__ == "__main__":
    main()
