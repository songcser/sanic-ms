#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from xmlrunner.unittest import TestProgram
from xmlrunner.runner import XMLTestRunner

if not os.path.exists("reports"):
    os.mkdir("reports")

if sys.argv[0].endswith("__main__.py"):
    import os.path
    # We change sys.argv[0] to make help message more useful
    # use executable without path, unquoted
    # (it's just a hint anyway)
    # (if you have spaces in your executable you get what you deserve!)
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + " -m xmlrunner"
    del os

__unittest = True

main = TestProgram

with open('reports/junit.xml', 'wb') as output:
    main(
        module=None, testRunner=XMLTestRunner(output=output),
        failfast=False, catchbreak=False, buffer=False)

