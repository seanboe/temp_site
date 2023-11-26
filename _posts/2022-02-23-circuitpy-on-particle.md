---
layout: post
current: post
cover: assets/images/particle-circuitpy.png
title: Converting particle devices to circuit python
categories: [ Miscellaneous ]
---

How to convert particle Xenon, Argon, and (theoretically) Boron devices to circuit python. 

After Particle mesh failed, I was left with 4 particle devices that couldn't do anything particularly special (but had a hefty price tag, mind you). After being urged to by my Dad, I used my new [openocd skills](https://seanboe.github.io/blog/using-openocd) to convert these devices to running the circuit python bootloader. It's actually super easy!

First, install openocd. On mac, you can use homebrew:

`brew install open-ocd`

Then, download the nrf52 (all of these particle devices use this processor) [bootloader from adafruit](https://github.com/adafruit/Adafruit_nRF52_Bootloader/releases). Look for a hex file that starts with particle and contains your board name - yes, the boards _are_ different. Then put this file in your working directory.

> This bootloader is precompiled for you - if you'd like to do it yourself (why?) then you can follow [these instructions](https://learn.adafruit.com/circuitpython-on-the-nrf52/build-flash-particle)

After that, still in your working directory, create a file called `openocd.cfg`. This is the openocd configuration file. Inside, put:

```zsh
source [find interface/cmsis-dap.cfg]
source [find target/nrf52-particle.cfg]

adapter_khz 1000

transport select swd

init
flash list
targets
# make sure that you're using the right hex file!
program particle_argon_bootloader.hex verify reset
shutdown
```

> This is using the particle debugger; if you are using something diffrent, then you will need to change the interface configuration file

Now, in the working directory and with the debugger and usb cable plugged into the microcontroller, run `openocd`. You should get a fairly long prompt output (that probably has your device's name instead of "little nrf52.cpu"):

``` zsh
Open On-Chip Debugger 0.11.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : auto-selecting first available session transport "swd". To override use 'transport select <transport>'.
DEPRECATED! use 'adapter speed' not 'adapter_khz'
Warn : Transport "swd" was already selected
Info : CMSIS-DAP: SWD  Supported
Info : CMSIS-DAP: FW Version = 1.10
Info : CMSIS-DAP: Interface Initialised (SWD)
Info : SWCLK/TCK = 1 SWDIO/TMS = 1 TDI = 0 TDO = 0 nTRST = 0 nRESET = 1
Info : CMSIS-DAP: Interface ready
Info : clock speed 1000 kHz
Info : SWD DPIDR 0x2ba01477
Info : nrf52.cpu: hardware has 6 breakpoints, 4 watchpoints
Info : starting gdb server for nrf52.cpu on 3333
Info : Listening on port 3333 for gdb connections
    TargetName         Type       Endian TapName            State       
--  ------------------ ---------- ------ ------------------ ------------
 0* nrf52.cpu          cortex_m   little nrf52.cpu          running

Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : accepting 'telnet' connection on tcp/4444
Info : nRF52840-xxAA(build code: C0) 1024kB Flash, 256kB RAM
Error: Target not halted

target halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x00000998 msp: 0x20000400
Info : Mass erase completed.
target halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0xfffffffe msp: 0xfffffffc
** Programming Started **
Info : Padding image section 0 at 0x00000b00 with 1280 bytes
Info : Flash write discontinued at 0x00025de8, next section at 0x000f4000
Warn : Adding extra erase range, 0x00025de8 .. 0x00025fff
Info : Padding image section 2 at 0x000fc160 with 5792 bytes
Warn : Adding extra erase range, 0x000fd858 .. 0x000fdfff
Warn : Adding extra erase range, 0x10001000 .. 0x10001013
Warn : Adding extra erase range, 0x1000101c .. 0x10001fff
** Programming Finished **
** Verify Started **
** Verified OK **
** Resetting Target **
shutdown command invoked
Info : dropped 'telnet' connection
```

But that means that it worked!

Now wait for the board to show up as a boot drive. Once it does, download the [uf2 file](https://circuitpython.org/downloads) and copy it into the boot drive. After a couple seconds, it will disappear and show up as `CIRCUITPY`. Now, double check that you used the right bootloader and uf2 files by looking at the `boot_info.txt` file and making sure that the board listed in there is correct.

### Potential mishaps

When converting my boards, I accidentally programmed a Xenon bootloader (and circuitpython uf2 file) onto an Argon board. This presents a slight issue, since the `nrf52-particle.cfg` openocd configuration will now not detect the device (because it's no longer a particle device!). Instead, you'll now need to use the `nrf52.cfg` configuration file (which applies to nrf52 mcus in general, as you'd might expect). But you'll also need to erase the chip prior to programming. Modify the configuration file by adding some commands:

``` zsh
init
flash list
targets

# new
reset halt
nrf5 mass-erase


# make sure that you're using the right hex file!
program particle_argon_bootloader.hex verify reset
shutdown
```

The `reset halt` is required for the `nrf5 mass-erase` command to work. This, as you might expect, completely erases the nrf52 (following [this documentation](https://openocd.org/doc/html/Flash-Commands.html)). After that, follow the same steps and you'll be able to set up the board correctly.

> When using openocd, it might be useful to use telnet for command-line-interface-like usage. Install telnet with homebrew: `brew install telnet` and then run `telnet 127.0.0.1 4444` in a separate terminal while running openocd. This way, you can manually type your commands instead of having to put everything inside of the configuration file. 
