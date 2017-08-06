#!/bin/bash
cd src
gunicorn app:app --daemon
python worker.py
