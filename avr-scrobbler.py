#!/usr/bin/env python
import pylast
import time
import pickle
import os
import socket
import sys
import getopt

BUFFER_SIZE = 1024
PICKLE_FILEPATH = os.path.join(
    os.path.expanduser("~"), ".avr-scrobbler.pickle")

try:
    AVR_IP = os.environ['AVR_IP']
    AVR_PORT = int(os.environ['AVR_PORT'])
except KeyError:
    AVR_IP = '192.168.1.157'
    AVR_PORT = 50000

try:
    API_KEY = os.environ['LASTFM_API_KEY']
    API_SECRET = os.environ['LASTFM_API_SECRET']
except KeyError:
    API_KEY = ""
    API_SECRET = ""

try:
    username = os.environ['LASTFM_USERNAME']
    password_hash = os.environ['LASTFM_PASSWORD_HASH']
except KeyError:
    username = "my_lastfm_user_name"
    password_hash = pylast.md5("my_lastfm_password")


def sendMessage(unit, command, arguments, verbose=False):
    timeout = 3.0
    retries = 5

    delay = timeout * 0.08

    while True:
        msg = unit + ":" + command + "=" + arguments
        msg += "\r\n"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((AVR_IP, AVR_PORT))
            s.send(msg)
            data = s.recv(BUFFER_SIZE)
            s.close
            return data.rstrip()
        except (socket.error, socket.timeout) as msg:
            # retry if AVR's server is busy with another client
            retries -= 1
            if not retries:
                return None

            delay += 0.08 * timeout

            print "No connection. Retrying in:", delay, " s."
            time.sleep(delay)


def initLastFM():
    return pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)


def save_state(state):
    with open(PICKLE_FILEPATH, "w") as handle:
        pickle.dump(state, handle)


def load_state():
    if os.path.exists(PICKLE_FILEPATH):
        with open(PICKLE_FILEPATH) as handle:
            return pickle.load(handle)

    return None


def parse_reply(line):
    return line[line.find("=") + 1:]

# a dictionary that defines mappings between information about music
# played on specific inputs by the AVR and what pylast's scrobble() needs
inps = {
    'Spotify': {'prefix': '@SPOTIFY', 'comms': {
        'Artist': 'ARTIST',
        'Album': 'ALBUM',
        'Track': 'TRACK',
        'Playbackinfo': 'PLAYBACKINFO'
    }},

    'SERVER': {'prefix': '@SERVER', 'comms': {
        'Artist': 'ARTIST',
        'Album': 'ALBUM',
        'Track': 'SONG',
        'Playbackinfo': 'PLAYBACKINFO'
    }},

    'USB': {'prefix': '@USB', 'comms': {
        'Artist': 'ARTIST',
        'Album': 'ALBUM',
        'Track': 'SONG',
        'Playbackinfo': 'PLAYBACKINFO'
    }}
}


def poll_input(inp):
    info = {}

    for field, command in inp['comms'].iteritems():
        while True:
            reply = sendMessage(inp['prefix'], command, "?")

            # sometimes we get not what we asked for
            if not reply.startswith(inp['prefix'] + ":ELAPSEDTIME"):
                break
            # else:
            #  print reply

        info[field] = parse_reply(reply)

    return info


def poll_receiver():
    state = sendMessage("@MAIN", "PWR", "?", False)
    if state != "@MAIN:PWR=On":
        return None

    state = sendMessage("@MAIN", "INP", "?", False)

    # check if the AVR's current input is one we know how to handle
    for i in inps:
        if state == "@MAIN:INP=" + i:
            return poll_input(inps[i])

    return None


lastfm = initLastFM()

if not lastfm:
    print "Unable to login to LastFM"
    sys.exit(1)

prev_info = load_state()

while True:
    info = poll_receiver()

    if info and info != prev_info and info["Playbackinfo"] != "Stop":
        lastfm.scrobble(
            artist=info["Artist"],
            album=info["Album"],
            title=info["Track"],
            timestamp=int(time.time())
        )

        print info['Artist'] + "," + info['Album'] + "," + info['Track']
        prev_info = info
        save_state(info)

    time.sleep(30)


# vim: ts=2 expandtab shiftwidth=2
