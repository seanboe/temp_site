---
layout: post
current: post
cover: assets/images/buck-oscilloscope.png
navigation: True
title: Simple Variable Buck Converter
date: 2022-7-13  10:18:00
class: post-template
subclass: 'post'
author: sean
---

Yesterday I built a variable buck converter for fun. It allows you to vary an output voltage from about 12V to 3V or less using PWM.

Here's the schematic:

![schematic](https://media.discordapp.net/attachments/881969144814256200/998654415525392517/Screen_Shot_2022-07-18_at_11.16.01_AM.png?width=1988&height=1138)


... and a picture of my setup:

![setup](https://media.discordapp.net/attachments/881969144814256200/998666356138446918/Screen_Shot_2022-07-18_at_12.03.28_PM.png)

In the picture, the transistor is on the left and the mosfet is on the right. I used small smd components (that are soldered to breakout boards) since I only need this for low current (< 1A) solutions and I want to eventually put this on a pcb. 

### How it works

A buck converter works by sending a PWM signal on the converter's main input voltage into a circuit involving an inductor and a capacitor. Since inductors restrict changes in current, as the voltage switches on and off, the inductor holds back the change slightly. As a result, the actual voltage passing through the capacitor stays roughly constant, somewhere between the maximum voltage and 0V. Since inductors are only current dependent, however, this is really only true when the load resistance stays constant. In the case that it isn't (assuming that the changes aren't _too_ great) and to continue smoothing the output voltage, a decoupling capacitor is added across the output lines. 

The final addition to the system is the flyback diode. This is to allow induced current from the inductor (whenever the current changes) to dissipate through the load and flow back into the inductor. Self-inductance causes inductors to act like a voltage / current source; the induced voltage has to be dissipated or else components can be damaged by ultra-high voltages (remember, inductors care only about current so low currents can result in high voltages for equal power). Flyback diodes are commonly used across the terminals of relays to preserve the relay as well as the load. 

<iframe width="560" height="315" src="https://www.youtube.com/embed/AVYg93VQCvA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


It was pretty fun to make and get working, however simple. My hope is that I'll be able to integrate it into OpenServo to vary the motor voltage... hopefully I'll post about that idea soon. 

##### Problems, for now:
Just don't run this at too high currents unless you want magic smoke to come out... 😂

### Update!
Someone commented on my youtube video with a question about using a transistor and 90V motor speed controller (along with a capacitor and diode) as a DC-DC converter for bucking 85V. The answer is that this totally works!

This is the schematic you would need:

![converter](https://media.discordapp.net/attachments/881969144814256200/1000517832540430377/Screen_Shot_2022-07-23_at_2.40.32_PM.png?width=1080&height=330)

This is a half-wave rectifier (which... rectifies AC voltage by taking only half of the wave) but with the mains voltage (in this case, 85V) as a PWM signal. The way that this works is that the transformer acts like the inductor in a buck converter circuit but has it's own step down depending on the output coil - input coil ratio. This means that the output voltage is dependent on the duty cycle of the switching (which would be done by the speed controller) and the transformer gain. 

You can use these components to make a half-wave rectifier, although it isn't actually doing any rectification in this case. 

To add better ripple rejection (this applies to the buck converter too!) more capacitors, of different types, can be added. It is best to also have the capacitances vary by a factor of 3; make one cap have 1/3 the capacitance of another.
