# hutton-helper development

A way to setup a dev environment for the HH Edmc Plugin. WARNING this is slightly outdated as EMDC is now on python3.x not 2.7

## Development Setup

Getting set up takes a few steps because EDMC is fussy, and because code editors like [Visual Studio Code][VSCode] need to see the modules EDMC provides while we're developing.

DON'T PANIC: these instructions are long only because

* We're trying to make it _really hard_ to screw up, and

* We're trying to leave your existing copy of Python unbroken

For the mug! Do this:

* Install [`git`](https://git-scm.com/download/win)

* Install the 32 bit version of Python 2.7 to `c:\Program Files (x86)\Python27`

  EDMC wants the 32 bit version. These instructions want that path. If you're willing to edit the path every time you cut and paste while you set up, no worries, put it anywhere you like. You'll only have to do it a few times.

  Don't over-write your existing Python! These instructions will help you leave it just how you like it.

* Download [`get-pip.py`](https://bootstrap.pypa.io/get-pip.py), e.g. to `%TEMP%`

* Install `pip`:

      "c:\Program Files (x86)\Python27\python.exe" "%TEMP%\get-pip.py" --user

* Install `virtualenv`:

      "c:\Program Files (x86)\Python27\python.exe" -m pip install virtualenv --user

* **Change directory to wherever your code lives**. If you don't know where that is:

      cd %HOMEPATH\Documents
      mkdir source
      cd source

* Clone [`EDMarketConnector`][EDMC] and [`hutton-helper`][HH]:

      git clone https://github.com/Marginal/EDMarketConnector.git
      git clone https://github.com/aarronc/hutton-helper.git

* Set up the virtual environment:

      cd hutton-helper
      "c:\Program Files (x86)\Python27\python.exe" -m virtualenv .

* Activate the virtual environment:

      Scripts\activate

  You'll `activate` each time you resume development. It sets everything up so you're using a copy of Python in `hutton-helper`. That 32-bit Python you set up will remain pristine, apart from `pip` and `virtualenv`. Your usual 64-bit copy of Python 3 won't be touched at all.

  Which is good, because now we need to get dirty.

* Install everything EDMC needs, plus a couple extras:

      cd ..\EDMarketConnector
      pip install -r requirements.txt
      pip install pylint pep8 rope

* Launch EDMC for a test:

      python EDMarketConnector.py

* Read the output in your command line window for the location of wherever you've had `hutton-helper` installed:

  > `Loading plugin hutton-helper from "C:\Users\sporebat\AppData\Local\EDMarketConnector\plugins\hutton-helper\load.py"`

* Shut down EDMC

* Start a new command window for the next few steps:

      start

* In that window, change directory to wherever `plugins` was above:

      cd "C:\Users\sporebat\AppData\Local\EDMarketConnector\plugins"

  If you're lucky, this'll work:

      cd "%LOCALAPPDATA%\EDMarketConnector\plugins"

* Disable that install of `hutton-helper`, then link in your development copy:

      ren hutton-helper hutton-helper.disabled
      junction "hutton-helper" "%HOMEPATH%\Documents\source\hutton-helper"

  (If your source code lives somewhere, you'll need to adjust that second command.)

* Throw away that command line window:

      exit

* **BASK IN HER GLORY**. You're all set up!

## VS Code Setup

To set up [Visual Studio Code][VSCode] for developing `hutton-helper`, install the [EditorConfig] and Python extensions:

    code --install-extension EditorConfig.EditorConfig
    code --install-extension  ms-python.python

Then, copy the following JSON to `.vscode\settings.json` in your `hutton-helper` directory:

```json
{
  "files.exclude": {
    "**/.git": true,
    "**/*.pyc": true,
    "Scripts": true,
    "Include": true,
    "Lib": true,
    "tcl": true
  },
  "python.pythonPath": "Scripts\\python.exe",
  "python.linting.enabled": true,
  "python.linting.pep8Enabled": true,
  "python.linting.pylintUseMinimalCheckers": false
}
```

Finally, create a `.env` file in `hutton-helper` containing:

    PYTHONPATH=..\EDMarketConnector

To launch your editor from that directory:

    code .

## Development

To resume development:

    cd "%HOMEPATH%\Documents\source\hutton-helper"
    Scripts\activate
    code .

[EDMC]: https://github.com/Marginal/EDMarketConnector
[HH]: https://github.com/aarronc/hutton-helper
[VSCode]: https://code.visualstudio.com/
[EditorConfig]: https://editorconfig.org/

## Release

    del *.zip
    python pack.py

... then upload the `.zip` file and `version.json` to the release directory.
