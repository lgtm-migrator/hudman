# HUD mirror script
Simple script to create a local HUD mirror, can be used with [SRC Repair](https://github.com/xvitaly/srcrepair) project.

# License
[GNU General Public License version 3](LICENSE). External libraries can use another compatible licenses.

# Requirements
 * Python 3.4+ with full set of standard libraries;
 * python-requests.

# Installation
 1. Clone this repository:
 ```bash
 git clone https://github.com/xvitaly/hudman.git hudman
 ```
 2. Install (in Python virtual environment):
 ```bash
 python setup.py install
 ```
 3. Run application:
 ```bash
 hudman --gamedb /path/to/hud/database.xml --outdir /tmp/hudman
 ```

# Available options
```
usage: hudman.py [-h] --gamedb GAMEDB --outdir OUTDIR
```

Optional arguments:
 * `-h` or `--help` - Show help message and exit;
 * `-y` or `--gamedb` - Specify path path to HUDs database file;
 * `-g` or  `--outdir` - Specify path to save downloaded files.
