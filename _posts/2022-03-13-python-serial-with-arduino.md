---
layout: post
current: post
cover: assets/images/python-serial-with-arduino.png
navigation: True
title: Talking to an Arduino over Serial with Python
date: 2022-03-13  10:18:00
class: post-template
subclass: 'post'
author: sean
---

How to use the python serial library to talk to an arduino from your computer!

Arduino microcontrollers usually have 1-2 TTL Serial ports that can be used to print to the Serial console (usually one isn't accessible) and another that can be used for interdevice communication. The one that interfaces with usb enables printing / reading from a Serial console on the arduino ide and is the one many programmers use for debugging and for providing input to a program. While it may seem like this port is locked up and accessible only to the arduino IDE, in reality, it just shows up as a normal, easy-to-use serial port on your computer with the TTL serial to RS-232 protocol conversion already finished which makes it incredibly easy to interface to using a python script and the [python pyserial library](https://pyserial.readthedocs.io/en/latest/pyserial.html).

First, plug in an arduino and make sure that it is showing up as a valid serial port. This can easily be done on mac by listing everything in the `/dev/` folder. Since the ports usually show up as `cu` (Call Up) devices, the search can be simplified using the grep command. Run `ls /dev/ | grep cu` and you should get something like this out:

``` shell
cu.Bluetooth-Incoming-Port
cu.usbmodem11101
cu.wlan-debug
```

The `usbmodem` device is, as you may guess, a usb device, and in this case, an Arduino! Now let's get working on a python script. First, install the pyserial library with:

``` shell
pip install pyserial
```

Now, create a working folder and a python file inside. Inside that file, let's open a serial port and set it up to send a message over it and print back a response:

```python
# import the serial library
import serial

# the port should be the one that you saw earlier
arduino = serial.Serial(port="/dev/cu.usbmodem11101", baudrate=115200, timeout=0.1)

# Get the user's input
message = input("Type your message")

# transmit the message; convert it to ascii encoding first, and then send it in bytes
arduino.write(bytes(message, 'ascii'))

# print out the response from the arduino
print(arduino.readline().decode('ascii').strip())

arduino.close()
```

Now let's work on the arduino side of things. The data sent by the python script to the arduino can be received using `Serial.readBytes()`. After that, we can send out the data with `Serial.write()`. Note that this is different than `Serial.print()` or `Serial.println()`; the former sends _bytes_ over the serial port, while the other sends _characters_. 

``` cpp
void setup() {
  // This must be the same baud rate as specified in the python serial object constructor
  Serial.begin(115200);
}

void loop() {

  // Check if there is something to receive
  if (Serial.available()) {

    // Create a buffer to read data into
    char buffer[100];

    // Clear the buffer
    memset(buffer, 0, sizeof(buffer));

    // Read all the bytes (the number returned by Serial.available() into the char buffer);
    Serial.readBytes(buffer, Serial.available());
    
    // Write back the serial data we got
    Serial.write(buffer);
  }
 
}
```

Upload that code to your arduino and run the python script from earlier, making sure not to open any serial interfaces to the arduino afterwards (don't open the serial monitor since the arduino can only interface to one port at a time). When you type some data, python should send that number to your arduino, which should receive it and send it back!

> The code above only uses c-strings, which are char arrays terminated by a null (\0) character that tells the array that it is a string and where to stop. In my opinion, these are much easier to work with than c++ Strings, since they are simpler and can be used with classic built-in functions like `atoi()`, `strcat()`, `strcpy()`, and more.

### Advanced Stuff

When using serial communication for a practical project (like building a command line interface... :D) it may be more practical to send and receive multiple numbers at a time. This functionality can easily be accomplished using `strtok()`, `atoi()` / `atof` and `sprintf()` on the arduino side. 

#### Recieving on the arduino

The first thing to point out is that it is easiest to send numbers from a python script to be received by the arduino using a comma-seperated message. Creating a message like this can easily be accomplished in python using a for-loop:

``` python
data = [1, 2, 3]
message = ""
for x in data:
  message = message + x + ","
message.strip(",")

# This will create a string that looks like this: "1,2,3"
```

In arduino, we can parse around the commas using `strtok()`. You can use a while-loop to find everything in the array and read it into a buffer, and then use `atoi()` (for converting characters to integer types) and `atof()` (for converting characters to floating-point types) in order to find everything:

``` cpp

// Let's assume that this is already full of data from a Serial.readBytes() command
char buffer[100];

// array to hold the data
double data[100];

// clear the data array
memset(data, 0, sizeof(data))

// the first argument of strtok() is the array to parse from (this can be replaced with NULL 
// if you want to use the same array as in a previous call), and the second is the token to parse around
char * num = strtok(buffer, ",");
int counter = 0;
while (num != NULL) {
  data[counter] = atof(num);
  strtok(NULL, ",");
  counter++;
}
```

This will read the numbers in a comma-seperated floating-point line into a double array.

#### Sending from an arduino

Sending multiple numbers from an arduino, also in a comma-seperated format, can be easily achieved using `sprintf()`. Note that if you're transmitting floating point numbers, it is easiest to cast the number to a c++ String and that to a c-string using `c_str()`. This is because the format specifier for a floating point number won't actually include the numbers after the decimal point... for some reason. Here is an example of how to do it correctly:

``` cpp
char output[100];
memset(output, 0, sizeof(buffer));

int integer1 = 10;
double double1 = 15.15;
int integer2 = 30;

// Create the formatted string; don't forget to use the _String_ format specifier for the floating point number!
// The number passed to the String() cast is the number of decimal places of the floating point number to include in the string
// in this case, this is 3
sprintf(output, "%d,%s,%d", integer1, String(double1, 3).c_str(), integer2);

// Transmit out
Serial.write(output);
```

After this, you can easily parse around this using python:
``` python
response = [float(x) for x in output.split(',') if x != '']
```

### Adding automatic port detection

implementing automatic port detection can be super useful when you have multiple usb ports on your computer (i.e. practically all computers). The key is to recognize the usb device "Product Name", which all arduinos have. To find the product name of your arduino, use this simple script:

``` python
import serial
import serial.tools.list_ports

available_ports = list(serial.tools.list_ports.comports())

for port in available_ports:
  print(port.description)
```

That should list out the names of all the usb devices you have connected, and your arduino should be one of them. For an Adafruit itsybitsy m0, for example, this will be printed out: `ItsyBitsy M0 Express` which makes sense, since this is the name specified in the [bootloader makefile configuration](https://github.com/adafruit/uf2-samdx1/blob/master/boards/QTPy_m0/board_config.h).

To actually select the port, use the `.device` attribute of the correct port. This will return the `cu.usbmodemblahblahblah` that you need to actually select the serial port and instantiate the constructor. You should get it from here!

### Debugging 

__Port doesn't show up__: Usually this can easily be fixed by resetting the arduino board and / or plugging in the usb cable again. It is also possible that you aren't using a data-capable usb cable and that your cable only supplies power. In this case, just try swapping out the cable until things start working. 

__Port is _still_ not showing up__: This happened to me after I had just burned a custom bootloader to one of my arduinos. I discovered that my bootloader had actually been corrupted and that the device wasn't accessible at all from the serial port, so my solution was the burn the bootloader again. Maybe this'll work for you?

__Wierd characters coming back__: This is likely because you are using an incorrect baud rate, and that the baud rate of the arduino and the python serial port are different. Just make sure that they are the same, and things should be fixed. 

__Python serial port times out__: This is due to having too low of a serial timeout (duh!) specified in the serial object constructor in python. Don't forget that the timeout is specified in seconds!

<hr>

### Problems, so far:
- None! This form of communication has been incredibly reliable for many of my projects. I'm currently using this technique on one of my greatest (and recent) projects, which I'm really excited for (I'll probably release a post about it within the next few months).