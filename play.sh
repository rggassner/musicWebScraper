#!/bin/bash
pkill -f "Xvfb :99 -ac"
Xvfb :99 -ac &
export DISPLAY=:99
./play.py
pkill -f "Xvfb :99 -ac"
