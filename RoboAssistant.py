#!/home/pi/googleassistant/bin/python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import threading
import LED

import argparse
import json
import os.path
import pathlib2 as pathlib

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

###
import logging
import re
import subprocess
import vlc
import youtube_dl
import voice.tts


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

ydl_opts = {
    'default_search': 'ytsearch1:',
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}
vlc_instance = vlc.get_default_instance()
vlc_player = vlc_instance.media_player_new()


def power_off_pi():
    print('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    print('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    print('My IP address is %s' % ip_address.decode('utf-8'))


def play_music(name):
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(name, download=False)
    except Exception:
        print('Sorry, I can\'t find that song.')
        return

    if meta:
        info = meta['entries'][0]
        vlc_player.set_media(vlc_instance.media_new(info['url']))
        print('Now playing ' + re.sub(r'[^\s\w]', '', info['title']))
        #voice.tts.say('Now playing ' + re.sub(r'[^\s\w]', '', info['title']))
        vlc_player.play()
###

WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""

threadLED = threading.Thread(target=LED.led_glow, args=())
def process_event(event):
    """Pretty prints events.

    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.

    Args:
        event(event.Event): The current event to process.
    """
    global threadLED

    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print()
        if not threadLED.isAlive():
            threadLED = threading.Thread(target=LED.led_glow, args=())
            threadLED.start()

    print(event)

    ###
    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'stopp':
            if vlc_player.get_state() == vlc.State.Playing:
                vlc_player.stop()
        elif text == 'power off':
            process_event(EventType.ON_CONVERSATION_TURN_FINISHED)
            power_off_pi()
        elif text == 'reboot':
            process_event(EventType.ON_CONVERSATION_TURN_FINISHED)
            reboot_pi()
        elif text == 'ip address':
            process_event(EventType.ON_CONVERSATION_TURN_FINISHED)
            say_ip()
        elif text == 'pause':
            process_event(EventType.ON_CONVERSATION_TURN_FINISHED)
            vlc_player.set_pause(True)
        elif text == 'resume':
            process_event(EventType.ON_CONVERSATION_TURN_FINISHED)
            vlc_player.set_pause(False)
        elif text.startswith('play '):
            # process_event(EventType.ON_CONVERSATION_TURN_FINISHED)
            play_music(text[5:])
###
    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        print()
        if threadLED.isAlive():
            threadLED.do_run = False
            threadLED.join()

    if event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
        if threadLED.isAlive():
            threadLED.do_run = False
            threadLED.join()

    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in event.actions:
            print('Do command', command, 'with params', str(params))


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--device-model-id', '--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=False,
                        help='the device model ID registered with Google')
    parser.add_argument('--project-id', '--project_id', type=str,
                        metavar='PROJECT_ID', required=False,
                        help='the project ID used to register this device')
    parser.add_argument('--device-config', type=str,
                        metavar='DEVICE_CONFIG_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'googlesamples-assistant',
                            'device_config_library.json'
                        ),
                        help='path to store and read device configuration')
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='path to store and read OAuth2 credentials')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + Assistant.__version_str__())

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    device_model_id = None
    last_device_id = None
    try:
        with open(args.device_config) as f:
            device_config = json.load(f)
            device_model_id = device_config['model_id']
            last_device_id = device_config.get('last_device_id', None)
    except FileNotFoundError:
        pass

    if not args.device_model_id and not device_model_id:
        raise Exception('Missing --device-model-id option')

    # Re-register if "device_model_id" is given by the user and it differs
    # from what we previously registered with.
    should_register = (
        args.device_model_id and args.device_model_id != device_model_id)

    device_model_id = args.device_model_id or device_model_id

    with Assistant(credentials, device_model_id) as assistant:
        events = assistant.start()

        device_id = assistant.device_id
        print('device_model_id:', device_model_id)
        print('device_id:', device_id + '\n')

        # Re-register if "device_id" is different from the last "device_id":
        if should_register or (device_id != last_device_id):
            if args.project_id:
                register_device(args.project_id, credentials,
                                device_model_id, device_id)
                pathlib.Path(os.path.dirname(args.device_config)).mkdir(
                    exist_ok=True)
                with open(args.device_config, 'w') as f:
                    json.dump({
                        'last_device_id': device_id,
                        'model_id': device_model_id,
                    }, f)
            else:
                print(WARNING_NOT_REGISTERED)

        for event in events:
            process_event(event)
