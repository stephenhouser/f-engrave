#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
PATH=".:$PATH" /usr/bin/env python f-engrave-154.py --fontdir /Library/Fonts --defdir ~/Documents
