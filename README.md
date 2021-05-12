# Google play python API [![Build Status](https://travis-ci.org/NoMore201/googleplay-api.svg?branch=master)](https://travis-ci.org/NoMore201/googleplay-api)

This project contains an unofficial API for google play interactions. The code mainly comes from
[GooglePlayAPI project](https://github.com/junus/googleplay-api/) which is not
maintained anymore. The code was updated with some important changes:

* ac2dm authentication with checkin and device info upload
* updated search and download calls
* select the device you want to fake from a list of pre-defined values (check `device.properties`)
(defaults to a OnePlus One)

# Usage

Check scripts in `test` directory for more examples on how to use this API.

```
from gpapi.googleplay import GooglePlayAPI

mail = "mymail@google.com"
passwd = "mypasswd"

api = GooglePlayAPI(locale="en_US", timezone="UTC", device_codename="hero2lte")
api.login(email=mail, password=passwd)

result = api.search("firefox")

for doc in result:
    if 'docid' in doc:
        print("doc: {}".format(doc["docid"]))
    for cluster in doc["child"]:
        print("\tcluster: {}".format(cluster["docid"]))
        for app in cluster["child"]:
            print("\t\tapp: {}".format(app["docid"]))
```

For first time logins, you should only provide email and password.
The module will take care of initalizing the api, upload device information
to the google account you supplied, and retrieving 
a Google Service Framework ID (which, from now on, will be the android ID of your fake device).

For the next logins you **should** save the gsfId and the authSubToken, and provide them as parameters
to the login function. If you login again with email and password, this is the equivalent of
re-initalizing your android device with a google account, invalidating previous gsfId and authSubToken.


## ❱ Installation

### Docker image

----------------------------------------------------------------------------------------

#### Official Docker Hub image

The [official googleplay-api Docker image](https://hub.docker.com/r/junus/googleplay-api)
is available on Docker Hub (automatically built from this repository):

```Shell
$ # Download the Docker image.
$ docker pull junus/googleplay-api
$ # Give it a shorter name.
$ docker tag junus/googleplay-api gapi
```

#### Install

If you downloaded the official image from Docker Hub, you are ready to use the tool so
go ahead and check the [usage instructions](#with-docker), otherwise execute the
following command in the previously created `googleplay-api/` directory (the folder
containing the `Dockerfile`) in order to build the Docker image:

```Shell
$ # Make sure to run the command in googleplay-api/ directory.
$ # It will take some time to download and install all the dependencies.
$ docker build -t gapi .
```

googleplay-api is now ready to be used, see the [usage instructions](#with-docker)
for more information.

### From source

----------------------------------------------------------------------------------------

#### Prerequisites

Apart from valid Google Play Store credentials, the only requirement of this project is
a working `Python 3` (at least `3.6`) installation and
[`pipenv`](https://pipenv.pypa.io/) (for dependency management).

#### Install

Run the following commands in the main directory of the project (`googleplay-api/`)
to install the needed dependencies:

```Shell
$ # Make sure to run the commands in googleplay-api/ directory.

$ # This project uses pipenv (https://pipenv.pypa.io/) for dependency management.
$ # It can be installed with the following command:
$ # python3 -m pip install pipenv

$ # Install googleplay-api's requirements (a virtual environment will be created).
$ pipenv install --deploy
```

googleplay-api is now ready to be used, see the [usage instructions](#with-source)
for more information.

## ❱ Usage

You should have a `env.list` file ready
to be used or env variables `GPAPI_GSFID` and `GPAPI_TOKEN`. The usage instructions depend on how you installed the tool.

### With Docker

A download directory has to be mounted, otherwise the
downloaded application won't be accessible to the host machine. If the current
directory (`${PWD}`) contains an `output/` folder, the
command to download an application with package name `com.application.example` becomes:

```Shell
$ docker run \
    --env-file ./env.list \
    -v "${PWD}/output/":"/app/Downloads/" \
    -p 8085:8085 \
    --name gapi -it gapi
```

Send request to `localhost:8085/process/com.application.example`,
if the download is successful, the resulting `.apk` file will be saved in the `output/`
folder contained in the directory where the command was run (type

### With source

In the main directory of the project (`googleplay-api/`), call the following
instruction using the package name of the app to be downloaded:

```Shell
$ pipenv run python flask_api.py
```

Send request to `localhost:8085/process/com.application.example`,
if the download is successful, the resulting `.apk` file will be saved in the
`googleplay-api/Downloads/` directory.