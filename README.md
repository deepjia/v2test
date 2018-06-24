# V2Test

[![Build Status](https://travis-ci.org/deepjia/v2test.svg?branch=master)](https://travis-ci.org/deepjia/v2test)

## Demo

<http://izlt.xyz>

demo/demo

## Introduction

V2Test is a lightweight data driven testing framework based on Python 3.

Now integrated with WebGUI: V2Test Management.

Engines:

* [UI] Selenium browser automation test.
* [HTTP] Requests HTTP interface test.
* [Shell] Shell command or bash/python/ruby/perl script test.
* [MySQL] MySQL database test.
* [Appium] Appium iOS/Android test.
* [Locust] Locust load test.

Modes:

* [Standalone] Run cases locally.
* [Receiver] Run cases received from senders and send report back.
* [Sender] Send cases to receivers and gather reports.

Todos:

* [Doc] Add guide for integration with Jenkins and Travis CI.
* [Doc] Documents for human beings.
* [Engine] Scripts for appium installation.
* [Engine] Add more actions to Locust load testing engine.
* [Engine] May add some unit test engine.
* [Framework] Add loop/repeat action. 

It's easy to develop new engines.

![login](https://user-images.githubusercontent.com/1452602/38806756-e9f8fb80-41ac-11e8-8f35-267807301e22.png)
![add](https://user-images.githubusercontent.com/1452602/38806771-f801eb38-41ac-11e8-8246-1d8379c4a994.png)
![testsuite](https://user-images.githubusercontent.com/1452602/39228744-3cec3b22-4892-11e8-877f-1aa8e421075c.png)
![run](https://user-images.githubusercontent.com/1452602/38806780-01bd271e-41ad-11e8-89d4-900be8f11757.png)
![reports](https://user-images.githubusercontent.com/1452602/38806777-fef1dd18-41ac-11e8-9e1c-448be8467652.png)
![case](https://user-images.githubusercontent.com/1452602/38806784-03e451b6-41ad-11e8-8a7f-994b9fd4511e.png)
![case](https://user-images.githubusercontent.com/1452602/31042295-3eac8c94-a56a-11e7-9f1f-d28d6ca45782.png)
![run](https://user-images.githubusercontent.com/1452602/31042321-de28731e-a56a-11e7-9cc6-97011b86624b.png)


## Prerequisites

Python 3.5+

## Installation

Install Git and Python 3.5+.

Then, clone the repo and install requirements:

```
git clone https://github.com/deepjia/v2test.git
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

### Local

```
./run.py
```
Run cases in `TestCases`. 

Test report will be generated in `TestReports`.

*LOG\_LEVEL* and *LEN\_MSG* are configurable in `config.ini`.

### Receiver

```
./receiver.py
```
Run cases in `TestCases` which are received from sender. 

Test report will be generated in `TestReports`, and send back to sender.

*PORT* is configurable in `config.ini`.

### Sender

```
./sender.py
```
Send cases in `RemoteReport/ReceiverName` to receivers and reports will be gathered in `RemoteReports`.

Set *ReceiverName=IP:PORT* in `config.ini`.

### WebGUI

```
./manager.sh
```
The default url:
<https://127.0.0.1:5000/>

## Structure

```
.
├── TestCases: Case files(xlsx).
│   └── Example.xlsx: Example for case file.
├── RemoteCases: Case files to send.
│   └── RECEIVER1: Case files to run in RECEIVER1.
│       └── Example.xlsx
├── TestEngines: V2Test engines.
│   ├── __init__.py
│   ├── config.py
│   ├── excel.py
│   ├── http.py
│   ├── linux32: UI driver for 32bit browser, Linux.
│   │   ├── chromedriver
│   │   └── geckodriver
│   ├── linux64: UI driver for 64bit browser, Linux.
│   │   ├── chromedriver
│   │   └── geckodriver
│   ├── mac64: UI driver for macOS.
│   │   ├── chromedriver
│   │   └── geckodriver
│   ├── shell.py
│   ├── ui.py
│   ├── win32: UI driver for 32bit browser, Windows.
│   │   ├── IEDriverServer.exe
│   │   ├── chromedriver.exe
│   │   └── geckodriver.exe
│   └── win64: UI driver for 64bit browser, Windows.
│       ├── IEDriverServer.exe
│       └── geckodriver.exe
├── TestFiles: Test files, for example scripts to run and files to upload.
│   └── example.sh: One example for test file, a shell script.
├── README.md: What you are reading.
├── TestReports: Test reports will be generated here.
├── RemoteReports: Test reports from receivers will be gathered here.
├── config.ini: Configuration for framwork and engines.
├── requirements.txt: Requirements generated by pip.
├── run.py: V2Test standalone mode, where local tests start.
├── sender.py: V2Test sender mode.
└── receiver.py: V2Test receiver mode..
```

## Usage - Framework

### Config

*LOG_LEVEL=INFO or DEBUG or WARNING or ERROR*

For most users, set *LOG_LEVEL=INFO*

### Case

V2Test will scan `TestCases` for all excel files, and load all cases with *Run = y* from all sheets.

One line is one step; Cases will be run step by step, and each case can have more than one lines.

*Run, Case ID, Case Name, Engine* should and should only be in the 1st line.

***Run***

Whether or not the case will be run. Set to ***y*** or ***n*** for the 1st line of each case.

(*Required* for each case)

***ID, Name***

Case/Logic/Model ID.
Case/Logic/Model Name.

(*Required* for each case/logic/model)

***Engine***

The engine for the case. 

Engine *ui, http, shell* are now built in. Engine *mysql* is coming soon.

(*Required* for each case)

***Locator/Encapsulator*** and ***Value***

Used to locate elements in web pages or encapsulate parameters.

***Action*** and ***Value***

Used to interact with engines (some with framework), which is also known as "keyword".

### Case - Action

***wait***

Wait for *value* seconds.

***equal\[.arg][.arg2]..., in\[.arg][.arg2]...***

Check whether *Value* equals or in the returned value.
*arg* is the attar of the returned value, or method defined in engines.

***!equal\[.arg], !in\[.arg], log\[.arg]***

*!* means not.
*log* is used to show the value.

You can refer to the examples in `TestCases`, it is easy to understand how to create test cases.

All settings are in `config.ini`.

***save_var\[.arg][.arg2]...***

Save the returned value into var ${*Value*}.

*arg* is the attar of the returned value, or method defined in engines.

***logic***

Call logic with the id of *Value*.

## Usage - UI Engine

### Config

***DRIVER=Safari***

Since OS X El Capitan, [safaridriver](https://webkit.org/blog/6900/webdriver-support-in-safari-10/)(macOS only) is preinstalled.

Keep Safari > Preferences > Show Develop checked.

Keep Develop > Allow Remote Automation checked.

Set *DRIVER=Safari* in `config.ini`

***DRIVER=IE, Firefox, Chrome***

Download [IEDriverServer](http://selenium-release.storage.googleapis.com/index.html) (Windows only), [geckodriver](https://github.com/mozilla/geckodriver/releases), [chromedriver](https://chromedriver.storage.googleapis.com/index.html), then unpack it and put the binary file in  `TestEngines/.../`

(Current version of binary is already there, but an update is recommended)

Set *DRIVER=IE or Firefox or Chrome*, *BIT=32 or 64* (depend on your browser) in `config.ini` 

***DRIVER=Remote***

(Untested)

Make sure [Standalone Selenium Server](http://www.seleniumhq.org/docs/03_webdriver.jsp#running-standalone-selenium-server-for-use-with-remotedrivers) is running.

Set *DRIVER=Remote, REMOTE\_SERVER=(url), REMOTE\_BROWSER=Chrome or Firefox or Safari* in `config.ini` 

***URL***

The default URL if *Value* of *Action=open* is null.

***WAIT*** 

Implicit waits, wait for *Value* seconds before before looking for elements.

### Case - Locator

***id, name, xpath, css_selector, class\_name, tag\_name, link\_text, partial\_link\_text***

Find elements by id, name, xpath etc.

***saved_elem***

Find previously saved elements. (Saved by the *save_elem* action.)

***model***

Find elements from models.

### Case - Action

***open, close***

Open the URL in *Value*, the default URL is in `config.ini`. Or close current browser window.

***type, press, click***

Input *Value* in text areas, or press Key *Value* of the keyboard, or click the element.

***[de]select\[.Key]***

Select/Deselect the option by *Key in ('value', 'visible_text', 'index')*


Select/Deselect all when *Key* and *Value* are null.

***within***

Explicit waits, wait for the element to appear, up to *Value* seconds.

***save_elem***

Save the element with the name *Value*, in order to be found by locator *saved_elem*.

***is_displayed, is_enabled, is_selected***

If the element is displayed/enabled/selected, return 'True'. Otherwise 'False'.

***get_attribute.Key***

Gets the given attribute or property of the element.
Eg: get_attribute.value

***get_property.Key***

Gets the given property of the element.

***text, tag_name***

Gets the text/tag_name of the element.

***switch_to.Key***

Switch to an element, frame etc.

## Usage - Appium Engine

### Config

Refer to the document of [appium](http://appium.io/slate/en/master/?python#).

### Case - Locator

***ios_uiautomation, android_uiautomator, ios_predicate, accessibility_id, class_name, xpath***

Refer to [finding-and-interacting-with-elements](http://appium.io/slate/en/master/?python#finding-and-interacting-with-elements) of appium.

***x, y***

(x, y) location of touch area.

### Case - Action

Refer to [automating-mobile-gestures](http://appium.io/slate/en/master/?python#automating-mobile-gestures) of appium.

***touch_action{***

***}***

All actions between *touch_action{* and *}* will run as a touch action chain.

***tap, press, long_press, move_to***

Touch actions that can be chained by *touch_action{* and *}* or be used standalone.

*Vaule* is count for *tap* or duration for *long_press*

***zoom, pinch, scroll***

Zoom, pinch or scroll to an element.

Actions of UI Engine can also be used.


## Usage - HTTP Engine

### Config

***BASEURL***

*BASEURL* is the base URL for *Value* without base URL, and the default URL for null *Value*

*TIMEOUT* is the default timeout for all requests.

### Case - Parameter

***headers, params, data, files ...{***

***}***

All *Parameter: Value* between *Tag{* and *}* will be encapsulated to dict: *Tag={Encapsulator1: Value1, Encapsulator2: Value2, ...}*, and added to the parameter of your request.

Nesting is supported.

***data, ...[***

***]***

All *Parameter: Value* between *Tag[* and *]* will be encapsulated to list: *Tag=[(Encapsulator1, Value1), (Encapsulator2, Value2), ...]*, and added to the parameter of your request.

Nesting is supported.

***files{}***

Specially, *files{}: Value* will be encapsulated to *files={'file': open(Value, 'rb')}*

***params, headers, data, timeout, ...***

Parameters of requests. *Value* should be valid python types, such as strings, numbers, tuples, lists, dicts, booleans, and None. For example, strings should be quoted.

### Case - Action

***get, post, (head, put, delete, options)***

Send HTTP requests with parameters to the *Value* URL.

***equal\[.arg][.arg2]..., in\[.arg][.arg2]...***

Check whether *Value* equals or in the returned value.
*arg* is the attar of the returned value, or method defined in engines.

For HTTP Engine, *arg=json* can conver json text to list/dict. Eg:

response = '[{"number": 1,"title": "Snapshot for README.md"}]'

*equal.json.0.title* means to compare *value* with 'Snapshot for README.md'

## Usage - Shell Engine

### Case - Action

***command***

Run shell command.

***bash/python/ruby/perl***

Run bash/python/ruby/perl script.

***file***

Run executable file.

## Usage - MySQL Engine

### Config

***HOST, USERNAME, PASSWORD, DATABASE, CHARSET***

Basic info of MySQL database.

### Case - Action

***commit***

Run SQL Query and commit.

***fetchone.\[\*]***

Run SQL Query and fetch one record, or fetch the value of key * from the record.

***fetchall.\****

Run SQL Query and fetch one records.

***fetchmany.\****

Run SQL Query and fetch as many as * records.

***sql***

Run SQL scrpit.

## Usage - Locust Engine

### Config

***CLIENT***

Default number of concurrent clients.

***RATE***

The default rate per second in which clients are spawned.

***NUMBER***

Default number of requests to perform.

***HOST***

Default host to load test in the following format: https://10.21.32.33

***BACKGROUND***

Set *BACKGROUND=Y* to run load tests in the background.

### Case - Parameter

***client/rate/number/host***

Normal parameters for action *file*.

### Case - Action

***file***

Run locust file.