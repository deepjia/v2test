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
Python3 with moudles:

selenium requests xlrd xlwt ddt html-testRunner

For macOS users, I recommend Homebrew and pip3 with `--user`:

```
brew install python3 git
pip3 install -r requirements.txt --user -U
PATH=$PATH:~/Library/Python/3.6/bin
git clone https://github.com/deepjia/v2test.git
```
## Structure
### config.ini
Configuration for framwork and engines.
### run.py
V2Test framework, where tests start.
### Cases
Case files in folder `Cases`, and there are examples.

`xlsx` recommended, and `xls` will be deprecated later.
### Files
Test files in folder `Files`, for example scripts to run and files to upload.
### Engines
V2Test engines here.
### Reports
Test reports will be generated here.
## Case Guide
Coming soon...

Now you can refer to the examples in `Cases`, it is easy to understand how to create cases.
## Usage
Edit `config.ini` and your cases, then:

```
./run.py
```
