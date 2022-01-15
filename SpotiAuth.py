from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import time
import signal
import requests
import json
import os
import secret
global token_response2


class SpotiAuth:

    def __init__(self):
        pass

    @staticmethod
    def get_auth_code():
        payload = secret.payload
        payload['grant_type'] = 'authorization_code'
        cmd = 'python -m http.server'
        process = subprocess.Popen(cmd)  # open localhost http server:
        # get the required code from the response url
        url = f'https://accounts.spotify.com/authorize?client_id={payload.get("client_id")}&response_type=code&' \
              f'redirect_uri={payload.get("redirect_uri")}&scope={payload.get("scope")}'
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url)

        i = 0
        p = 0
        codeurl = ''
        while i == 0 and p < 42:
            codeurl = driver.current_url
            time.sleep(2)
            if '8000/?code=' in codeurl:
                codeurl = str(driver.current_url)
                i = 1
            else:
                p += 1
        code_intermediate1 = codeurl.split("=")[1]
        code = code_intermediate1.split("#")[0]
        process.send_signal(signal.SIGTERM)    # terminate server
        print("Successfully Obtained Authorization Code.")
        driver.close()
        return code

    @staticmethod
    def get_token(code):
        if len(code) < 2:
            raise ValueError("Failed to obtain required code. Received empty string from function: get_auth_code().")
        else:
            payload = secret.payload
            payload['code'] = str(code)
            r = requests.post('https://accounts.spotify.com/api/token', data=payload)
            response = r.json()
            with open('Auth_token.json', 'w+', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=4)
            return None

    @staticmethod
    def refresh_auth(r_token):  # to run every 50 minutes to refresh the access token

        payload = secret.payload
        payload['grant_type'] = 'refresh_token'
        payload['refresh_token'] = str(r_token)
        r = requests.post('https://accounts.spotify.com/api/token', data=payload)
        refresh_response = r.json()
        return refresh_response

    @staticmethod
    def initializer():
        print('\nInitializing...\n')

        if os.path.isfile('Auth_token.json'):
            with open('Auth_token.json', 'r', encoding='utf-8') as f:
                token_response1 = json.load(f)
                token_refresh = token_response1.get('refresh_token')
            token_response = SpotiAuth.refresh_auth(token_refresh)
            token_response3 = token_response

        else:
            auth_code = SpotiAuth.get_auth_code()
            SpotiAuth.get_token(auth_code)
            with open('Auth_token.json', 'r', encoding='utf-8') as f:
                token_response = json.load(f)
                token_response3 = token_response
        print('\nInitialized.\n')
        return token_response3

    @staticmethod
    def recursive_reinit(token, first_start):
        global token_response2
        if first_start is True:
            token_response2 = token
            first_start = False
        else:
            pass
        time.sleep(3000)
        token_response2 = SpotiAuth.initializer()
        return SpotiAuth.recursive_reinit(token_response2, first_start)

    @staticmethod
    def currently_playing(token):
        current_song_url = 'https://api.spotify.com/v1/me/player/currently-playing'
        try:
            current_song_data = requests.get(current_song_url, params=token).json()
            song_name = current_song_data.get('item', {}).get('name')
            artist_name_data = []
            artist_name_data.extend(current_song_data.get('item', {}).get('artists'))
            artist_name = [i['name'] for i in artist_name_data if 'name' in i]
            is_playing = True
            return song_name, artist_name[0], is_playing
        except json.decoder.JSONDecodeError:
            song_name = ''
            artist_name = ['']
            is_playing = False
            return song_name, artist_name[0], is_playing
        except TypeError:
            # If file exists, delete it #
            if os.path.isfile("Auth_token.json"):
                os.remove("Auth_token.json")
            else:  # If not, show an error #
                raise TypeError('An unexpected TypeError was raised.')

