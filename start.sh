#!/bin/bash
python -m gunicorn -w 4 -b :$PORT app:app
