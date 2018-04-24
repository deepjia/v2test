#!/usr/bin/env python3
import os
from TestMgr import create_app
app = create_app(os.getenv('V2TEST_CONFIG') or 'default')

if __name__ == '__main__':
    app.run()