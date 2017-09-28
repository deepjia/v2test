# V2Test
## Introduction
V2Test is a lightweight data driven testing framework based on Python 3.

Engines:

* [UI] Selenium browser automation test.
* [HTTP] Requests HTTP interface test.
* [Shell] Shell command/script test.
* [DB] MySQL database test. - Coming later...

It's easy to develop new engines.

## Prerequisites
Python3 with modules:

selenium requests xlrd xlwt ddt html-testRunner
## Installation
Install Git and Python 3. Homrebrew is recommended for macOS.
Then, clone the repo:

```
git clone https://github.com/deepjia/v2test.git
```
For macOS, I recommend pip3 with `--user` so that `sudo` is unnecessary:

```
pip3 install -r requirements.txt --user -U
PATH=$PATH:~/Library/Python/3.6/bin
```

For Linux with Python 3 installed:

```
pip3 install -r requirements.txt
```

For Windows with Python 3 and pip installed:

```
pip install -r requirements.txt
```
## Structure
#### config.ini
Configuration for framwork and engines.
#### run.py
V2Test framework, where tests start.
#### Cases
Case files in folder `Cases`, and there are examples.

`xlsx` recommended, and `xls` will be deprecated later.
#### Files
Test files in folder `Files`, for example scripts to run and files to upload.
#### Engines
V2Test engines here.
#### Reports
Test reports will be generated here.
## Usage
(Coming soon...)

Now you can refer to the examples in `Cases`, it is easy to understand how to create test cases.

All settings are in `config.ini`.

Once finished:

```
./run.py
```
Test report will be generated in `Reports`.
## Engine: UI
#### Safari Driver (macOS only):

Ensure that the Develop menu is available. (Safari > Preferences > Show Develop)

Enable Remote Automation in the Develop menu. (Develop > Allow Remote Automation).

Always set DRIVER=Safari, BIT=64 in config.ini

### IE Driver (Windows only):

Download [IEDriverServer](http://selenium-release.storage.googleapis.com/index.html), unpack and put IEDriverServer.exe in `./Engines/win32` or `./Engines/win32`
Set DRIVER=ie, BIT=32 or BIT=64 in config.ini (Depend on your browser)

### Firefox Driver:
Download [IEDriverServer](http://selenium-release.storage.googleapis.com/index.html), unpack and put IEDriverServer.exe in `./Engines/win32` or `./Engines/win32`
Set DRIVER=Firefox, BIT=32 or BIT=64 in config.ini (Depend on your browser)

### Chrome Driver:
Download [geckodriver](http://selenium-release.storage.googleapis.com/index.html), unpack and put IEDriverServer.exe in `./Engines/win32` or `./Engines/win32`
Set DRIVER=Firefox, BIT=32 or BIT=64 in config.ini (Depend on your browser and your )