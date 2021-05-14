#!/usr/bin/env python3

import logging
import os
import re
import json
from requests.exceptions import ChunkedEncodingError

from flask import Flask, make_response, jsonify, abort, send_from_directory

from gpapi.googleplay import GooglePlayAPI

if "LOG_LEVEL" in os.environ:
    log_level = os.environ["LOG_LEVEL"]
else:
    log_level = logging.INFO

# Logging configuration.
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=log_level,
)
logging.getLogger("werkzeug").disabled = True


if 'ACCOUNTS' not in os.environ and 'accounts' not in os.environ['ACCOUNTS']:
    exit(1)
else:
    accounts = json.loads(os.environ['ACCOUNTS'])
indx = 0

# Directory where to save the downloaded applications.
downloaded_apk_location = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "Downloads"
)

# https://developer.android.com/guide/topics/manifest/manifest-element#package
package_name_regex = re.compile(
    r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$", flags=re.IGNORECASE
)


def create_app():
    app = Flask(__name__)
    # Create the download directory (if not already existing).
    if not os.path.isdir(downloaded_apk_location):
        os.makedirs(downloaded_apk_location)
    return app


application = create_app()


@application.errorhandler(500)
def application_error(error):
    logger.error(error)
    return make_response(jsonify(str(error)), error.code)


@application.route("/process/<package_name>", methods=["GET"], strict_slashes=False)
def process(package_name):
    if package_name_regex.match(package_name):
        try:
            account = _get_account()
            gsf_id = int(account['gsf_id'])
            auth_sub_token = account['token']

            server = GooglePlayAPI(account['lang'], account['timezone'], device_codename=account['device'])
            server.login(None, None, gsf_id, auth_sub_token)

            try:
                # server.log(package_name)
                fl = server.download(package_name)

                filename = "%s_%s(%s).apk" % (package_name, fl.get('versionString'), fl.get('versionCode'))
                downloaded_apk_file_path = os.path.join(
                    downloaded_apk_location,
                    filename,
                )

                with open(downloaded_apk_file_path, "wb") as apk_file:
                    for chunk in fl.get("file").get("data"):
                        apk_file.write(chunk)

                return {
                    "package": package_name,
                    "filename": filename,
                    "version": fl.get('versionString'),
                    "version_code": fl.get('versionCode')
                }

            except ChunkedEncodingError:
                logger.error(
                    f"An error during the download "
                    f"package name '{package_name}'",
                )
                return jsonify({
                    "package": package_name,
                    "status": "download error"
                }), 400
            except AttributeError:
                logger.error(
                    f"Unable to retrieve application with "
                    f"package name '{package_name}'",
                )
                return jsonify({
                    "package": package_name,
                    "status": "not valid"
                }), 400

        except Exception as e:
            logger.critical(f"Error during the download: {e}")
            abort(500)
    else:
        logger.critical("Please specify a valid package name")
        abort(400, description='Not valid package')


@application.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory=downloaded_apk_location, filename=filename)


def _get_account():
    global indx
    if len(accounts['accounts']) == indx:
        indx = 0
    acc = accounts['accounts'][indx]
    indx += 1
    return acc


if __name__ == "__main__":
    from waitress import serve
    serve(application, host="0.0.0.0", port=8085)
