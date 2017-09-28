# V2Test
## Introduction
V2Test is a lightweight data driven testing framework based on Python 3.

Engines:

* [UI] Selenium browser automation test.
* [HTTP] Requests HTTP interface test.
* [Shell] Shell command/script test.

It's easy to develop new engines.

To do:

* MySQL Engine. (Coming later...)
* More actions for UI Engine.
* Remote mode. 

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
## Usage - Framework
(Coming soon...)

Now you can refer to the examples in `Cases`, it is easy to understand how to create test cases.

All settings are in `config.ini`.

Once finished:

```
./run.py
```
Test report will be generated in `Reports`.
## Usage - UI Engine
### Driver
#### Safari Driver (macOS only):

Since OS X El Capitan, [safaridriver](https://webkit.org/blog/6900/webdriver-support-in-safari-10/) is preinstalled.

Keep Safari > Preferences > Show Develop checked.

Keep Develop > Allow Remote Automation checked.

Set *DRIVER=Safari*, *BIT=64* in `config.ini`

#### IE/Firefox/Chrome Driver:

Download [IEDriverServer](http://selenium-release.storage.googleapis.com/index.html) (Windows only), [geckodriver](https://github.com/mozilla/geckodriver/releases), [chromedriver](https://chromedriver.storage.googleapis.com/index.html).

Unpack and put the executable file in  `Engines/.../`

Set *DRIVER=IE or Firefox or Chrome*, *BIT=32 or 64* in `config.ini` (Depend on your browser)

#### Locator：
Locator is used to find elements in web pages.

***id, name, xpath, css_selector, class\_name, tag\_name, link\_text, partial\_link\_text***

Find elements by id, name, class name

***saved***

Find previously saved elements. (Saved by the ***save*** action.)
