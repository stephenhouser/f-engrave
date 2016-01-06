#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
PATH=".:/usr/local/bin:$PATH" /usr/bin/env python3 f-engrave-154.py --fontdir /Library/Fonts --defdir ~/Documents
