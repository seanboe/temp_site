---
layout: post
current: post
cover: assets/images/openocd.png
navigation: True
title: OpenOCD for burning bootloaders
categories: [ OpenServo ]
---

A short explanation on how to use openocd to program the bootloader of an atmega samd21.

For one of my upcoming projects, I'll be building a little pcb to interface with some sensors and do some computations. The problem is that this thing is really small, roughly 2x2 centimeters, and needs to have a fully arduino-compatible interface as well as a number of other peripherals on board, so I need to make my own arduino. This means that I need to burn my own bootloader onto the chip, but without using programming peripherals that arduinos are normally equipped with. While this addition would make things easier, I don't have room on my board to make this work. The solution to this is to program the processor (I chose the atsamd21, a widely supported chip in the arduino community) directly over an SWD connection using a debugger. How to interface to the debugger? Well, that's where this post comes in; using openocd!

OpenOCD (open on chip debugger) allows you to interface to a variety to debuggers and processors; it mushes the debugger and processor together, even when they aren't designed for each other sometimes.

For this post, I'm going to explain how I got this working and and then a system that completely didn't work (so that you don't fall into the same pit that I do).

### OpenOCD using the Particle Debugger

My method of getting this working was by using the [particle debugger](https://docs.particle.io/datasheets/accessories/debugger/) which I had lying around. While particle doesn't make this anymore, it appeared that it worked very similarly to the [ST-link](https://www.mouser.com/ProductDetail/Adafruit/2548?qs=SElPoaY2y5K%252BwHNUAvyTvg%3D%3D&mgh=1&gclid=Cj0KCQiAjc2QBhDgARIsAMc3SqSzy66xUxrKwRnrvJE0uKP9VPn1LcG0QoVwNc76ceQrU3iCMSSetYYaAi5XEALw_wcB), which is very popular and in stock practically everywhere.

The first thing to do is to install openocd. For mac, this is:

`brew install open-ocd`

Then, download a bootloader for your chip (I'm using [adafruit's itsybitsy m0 bootloader](https://github.com/adafruit/uf2-samdx1), which is for the at91samd21g18) and place it in a new directory. Then create a new file called `openocd.cfg`. You file structure should look like this:

bootloaders <br>
└── [bootloader file].bin<br>
└── openocd.cfg<br>

Now we need to edit the configuration file. This how openocd figures out how to mush everything together: you must specify the debugger, the target, and the transport protocol (i.e. swd) you are using, as well as (optionally) commands to run at initialization. Inside the configuration file put:

``` zsh
# Define the debugger interface
source [find interface/cmsis-dap.cfg]

# Define the communication speed
adapter speed

# Define the transport protocol
transport select swd

# Define the target
source [find target/at91samdXX.cfg]

# Intial commands
init
flash list
targets
```

Now we need to make the hardware connections. For this, it might be easiest to use an [swd connector breakout board](https://www.adafruit.com/product/2743) since swd connectors are small. Here are the connections that need to be made:

| SWD / Debugger | Pin |
| ----------- | ----------- |
| SWDIO | SWDIO |
| SWDCLK | SWDCLK |
| GND | GND |
| VREF | MCU Power |

This is what my setup looks like, if it helps:

![setup](https://media.discordapp.net/attachments/881969144814256200/945386778473410600/1B802925-38F4-4A90-A7D7-8A58D920BCE7.jpg?width=614&height=460)

Then plug in the debugger, navigate to the director with the configuration file and your bootloader, and run `openocd`. You should see this in the terminal:

``` zsh
Open On-Chip Debugger 0.11.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : CMSIS-DAP: SWD  Supported
Info : CMSIS-DAP: FW Version = 1.10
Info : CMSIS-DAP: Interface Initialised (SWD)
Info : SWCLK/TCK = 1 SWDIO/TMS = 1 TDI = 0 TDO = 0 nTRST = 0 nRESET = 1
Info : CMSIS-DAP: Interface ready
Info : clock speed 400 kHz
Info : SWD DPIDR 0x0bc11477
Info : at91samd.cpu: hardware has 4 breakpoints, 2 watchpoints
Info : starting gdb server for at91samd.cpu on 3333
Info : Listening on port 3333 for gdb connections
    TargetName         Type       Endian TapName            State       
--  ------------------ ---------- ------ ------------------ ------------
 0* at91samd.cpu       cortex_m   little at91samd.cpu       running

Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
```

You are now successfully running openocd! In order to run commands, you have two options: either continue putting them in the configuration file, or telnet into openocd (see the last line in the prompt output?) for a cli-like interface. For that, you must install telnet:

`brew install telnet`

Then open a new terminal window and run:

`telnet 127.0.0.1 4444`

You should get:

``` zsh 
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Open On-Chip Debugger
```

and in the terminal running openocd,

``` zsh
Info : accepting 'telnet' connection on tcp/4444
```

Now you can start typing commands directly to openocd. Through the telnet connection. This is very handy for debugging the debugger (making sure that openocd works) and that your connections are corrent, since you can try lots of stuff out, and, in my case, break one of your boards...

For reference, here is a diagram that describes the overarching connections being made (ignore the Jtag interface): 
![diagram](https://media.discordapp.net/attachments/881969144814256200/945376924438499348/Screen_Shot_2022-02-21_at_9.50.17_AM.png?width=420&height=460)

There is a vast directory of commands that openocd supports; they have a [general directory](https://openocd.org/doc/html/General-Commands.html) as well as a [processory specific directory](https://openocd.org/doc/html/Flash-Commands.html), but here is a short list of commands that I found useful.

__reset__: Performs a hard reset on the target

__reset halt__: Performs a hard reset on the target and halts it. Most commands require the target to be halted (like the `bootloader` commands). Exit from the halt with `reset` or `resume`

__at91samd bootloader__: This is an mcu-specific command. It returns the size configuration of the bootloader; if the bootloader that you are trying to program is larger than what is returned by this command, then the program will fail (bootloader protection)

__at91samd bootloader [size]__: This is the counterpart to the `at91samd bootloader` command and allows you to configure the maximum bootloader size. You can also use this to turn off bootloader protection by setting size to 0. It is recommended by documentation to turn bootloader protection back on once programming is finished

__at91samd chip-erase__: This is another mcu-specific command. It performs a complete erase of the chip, effectively factory reseting it. If you are running a program in the target and then run this command in openocd, the program will be erased.

__program bootloader-itsybitsy_m0-v3.14.0.bin__: This programs the bootloader onto the target. For this to work, the bootloader must be in the same directory as your configuration file. Additionally, you may add `verify` at the end of the command in order to verify that the programming was successful. 

__exit__: This closes the telnet session without terminating openocd processes. 

__shutdown__: Shuts down all openocd processes. Alternatively, you can terminate with control-c on mac. *__You must shutdown before disconnecting the bootloader__*!

Now let's get to programming the bootloader. While you can do this all manually through telnet, I find it easier put everything in the configuration file, since this will (in theory) be repeated.

In your configuration file, add:

``` zsh
reset halt
at91samd bootloader 0
program bootloader-itsybitsy_m0-v3.14.0.bin verify
at91samd bootloader 8192
reset
shutdown
```

> 8192 (the bootloader size) is the maximum size allocated for the bootloader in flash memory by the Arduino system.

After `targets`. Then run openocd. You should hopefully receive this output:

``` zsh
Open On-Chip Debugger 0.11.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : CMSIS-DAP: SWD  Supported
Info : CMSIS-DAP: FW Version = 1.10
Info : CMSIS-DAP: Interface Initialised (SWD)
Info : SWCLK/TCK = 1 SWDIO/TMS = 1 TDI = 0 TDO = 0 nTRST = 0 nRESET = 1
Info : CMSIS-DAP: Interface ready
Info : clock speed 400 kHz
Info : SWD DPIDR 0x0bc11477
Info : at91samd.cpu: hardware has 4 breakpoints, 2 watchpoints
Info : starting gdb server for at91samd.cpu on 3333
Info : Listening on port 3333 for gdb connections
target halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x00000294 msp: 0x20002de0
target halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x00000294 msp: 0x20002de0
** Programming Started **
Info : SAMD MCU: SAMD21G18A (256KB Flash, 32KB RAM)
** Programming Finished **
** Verify Started **
** Verified OK **
shutdown command invoked
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
```

Which means that you successfully burned a bootloader!

> The configuration above should work exactly the same for all at91samd processors, as long as you have a correct bootloader.

If you _did not_ receive this output, then there could be a couple problems. Assuming that openocd didn't return a cohesive error and instead said something like:

``` zsh
in procedure 'init' called at file "openocd.cfg", line 25
in procedure 'ocd_bouncer'
```

that either times out or decides to do nothing (I hope you can tell how frustrating those problems were for me), then you likely have a wiring issue, where the target can't communicate to the debugger properly. 

### What didn't work

Initially, I used the Olimex Arm-usb-ocd-h JTAG debugger with a JTAG-swd adapter from adafruit. Here is the config file I used for testing:

``` zsh 
source [find interface/ftdi/olimex-arm-usb-ocd-h.cfg]
source [find interface/ftdi/olimex-arm-jtag-swd.cfg]

source [find target/at91samdXX.cfg]

# # did not yet manage to make a working setup using srst
# #reset_config srst_only
# #reset_config  srst_nogate

adapter_khz 100

init
targets
reset halt
```

There are two things to notice. First, this debugger uses ftdi drivers which aren't installed on macos by default, and second, that I need to define the jtag-swd adapter as an interface. The former posed an immediate problem, since the drivers require SIP (system integrity protection) to be disabled. This is __not__ a good idea, since it protects the mac from malware, so I decided to use a jetson nano to do the programming instead. Basically, my setup looked like this: mac ssh &#8594; jetson nano &#8594; olimex debugger &#8594; jtag - swd adapter &#8594; target. This was slightly frustrating, but the ssh system seemingly worked well. The latter (that I needed to define the adapter as an interface) is meant to point out that the transport protocol can be set within a seperate configuration file, in this case the configuration file of a device. This meant that I didn't need to specify `transport select swd` like before.

Anyway, this didn't work, and I kept on getting this as my prompt output:

``` zsh
Open On-Chip Debugger 0.11.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : FTDI SWD mode enabled
DEPRECATED! use 'adapter speed' not 'adapter_khz'
Warn : libusb_detach_kernel_driver() failed with LIBUSB_ERROR_ACCESS, trying to continue anyway
Info : clock speed 1000 kHz
Error: Error connecting DP: cannot read IDR


Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
```

While openocd did run (for a long time I received only failed initilization responses) the `Error connecting DP` seemingly blocked all operations; they all responded with the same error and failed. The Olimex debugger documentation was quite old,so it's possible that just wasn't updated for my version of openocd, 0.11.0. 

<hr>

### Problems / updates

After a little bit of testing, I found an odd problem; a reset immediately after programming will cause something (the bootloader, I guess?) to break. The rgb LED on the itsybitsy m0 that I was using for testing would turn red and the led on pin 13 would flash. After shutting everything down, the itsybitsy would fail to turn on and wouldn't show up as an available usb port. Odd? The only "solution" I could find to this was to reprogram the bootloader twice, turn on bootloader protection, shut down openocd, power the device through it's own usb cable, and _then_ disconnect the debugger. When the debugger (which was powering the target at first) was removed, the mcu would then remain on in it's "red" state, but after a reset, everything was back to normal and the device would show up as a serial port again. As for why this works, I have absolutely no idea, but the moral of the story is to not mess around too much. 

I'm interested in making my own bootloader, since it would be really cool both to learn how to do it (dark magic has always been interesting to me) but also to be able to configure bootloaders to the exact device that they are being used on, in the case that I make a custom device (like for this project). Just changing the product name (this is what it is called in the makefile) would be neat, since everything would seem a million times more official then :D although it may then not be detected by the IDEs that I'm using. Regardless, so far, this method of bootloader programming seems to work well, and I'll be testing it on other processors soon!