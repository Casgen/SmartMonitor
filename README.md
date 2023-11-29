# Smart Monitor
---

An application for monitoring your property with Raspberry Pi and its camera module.

## Setup

Install the needed packages on Raspberry Pi.


```shell
$ sudo apt install -y python3-libcamera python3-kms++ libcap-dev python3-prctl libatals-base-dev ffmpeg python3-pip

$ python3 -m venv --system-site-packages <name-of-your-env>
$ pip install -r requirements.txt
```

For the Dev environment libcamera has to be built from source

```shell
$ sudo wget -qO /usr/local/bin/ninja.gz https://github.com/ninja-build/ninja/releases/latest/download/ninja-linux.zip # in order to be able to get ninja

$ sudo apt install ninja-build    # On Debian/Ubuntu
$ pacman -S ninja                 # On Arch

$ sudo apt install build-essential meson libyaml-dev python3-yaml python3-ply python3-jinja2 libssl-dev openssl git
$ git clone https://git.libcamera.org/libcamera/libcamera.git
$ cd libcamera
$ meson setup build
$ ninja -C build install
```

## Debugging

in order to debug in neovim, you need to install mfussenegger/nvim-dap and also install debugpy with pip.
**Make sure that you activate your python environment beforehand!**

```shell
$ pip install -m debugpy
```

you also need to setup the debugpy's adapter and create a configuration in the neovim lua files.


```lua
local dap = require "dap"

dap.adapters.python = {
    type = "executable",
    command = "./env/bin/python",
    args = {"-m", "debugpy.adapter"}
}

dap.configurations.python = {
    {
        name = "Python: Current File",
        type = "python",
        request = "launch",
        program = "${file}",
        console = "integratedTerminal",
        cwd = "${workspaceFolder}",
        justMyCode = true,
    },
}
```
