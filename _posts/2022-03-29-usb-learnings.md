---
layout: post
current: post
cover: assets/images/usbhubcover.png
title: Stuff I Learned about USB
categories: [ Team Inspiration, PCBs ]
---

USB communication is a standard in our daily lives with practically every computer and even microcontroller supporting some form of it. On my robotics team, I was asked to build a printed circuit board with a large, integrated usb hub that supported USB 3.0 and USB 2.0, so I began researching usb specification and ways that I could make this work. Unfortunately, due to the competition that this was meant for being cancelled, I no longer need to build it, so instead, I'm posting this to recap everything I've learned so far in case I forget; hopefully, this will be interesting to you too!

The first thing I did was choose a usb hub chip that supported more than 6 ports. I ended up using the [USB5537](https://www.digikey.com/en/products/detail/microchip-technology/USB5537-AKZE/3873213), which supports 4 USB 3.0 ports and 3 USB 2.0 ports and has integrated termination resistors (which is really nice). Although the chip is no longer manufactured, the [newer version](https://www.digikey.com/en/products/detail/microchip-technology/USB5537-AKZE/3873213) supports many features that were unnecessary for our use (like USB 3.1 instead of 3.0 and microchip's PortSwap functionality), and since we're manufacturing the hub in small quantities (less than 5 probably), this didn't matter. 

![strapping options](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/usbhubController.png?raw=true)

After reading the 72-page datasheet, I condensed the information into a [4 page google document](https://docs.google.com/document/d/1odN4gN_-jIQHQlAnRAWSDu5GT4It5h0y8beZlxaTd3k/edit). One of the great features of this chips is that it supports strapping options on the overcurrent sense and power port control pins that allows you to select whether you want each port to have overcurrent sense, port swapping, or battery powering enabled. The strapping options are a hardware enable / disable, but the chip will also read the state of each pin on startup and enable / disable functionality itself as well. This replaces the need for an external SPI ROM chip or an SMBus (which is similar to I2C) peripheral.

Then I spent time making a schematic for the board:

![schematic](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/usbcontroller.png?raw=true)

### Differential pairs

USB communication utilizes a differential pair for communication. Differential pairs are cool because they are an elegant way to eradicate common-mode noise from a system, which can be created by switches (for me, this means switching regulators) and high current lines, which can induce large and varying magnetic fields that will induce unpredictable currents (you'll see why this was important for me later). 

Understanding how a differential pair works requires understanding how noise can infect a signal on a single trace. If a signal is carried on a single trace or cable, then noise can induce unpredictable voltages onto the line, which can cause the signal to be compromised. A differential pair solves this problem by sending the same signal on one line and its inverse on another, with receivers measuring the diffence in potentials on each line. As long as the two traces are close together, most of the noise induced in one trace will be induced in the other, however in the same direction. This means that the difference in potentials on the traces will always be equal, and the signal won't be compromised!

![differential pairs](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT5tHk0NeUfwEB8Soyq3q8Y1YedaT8usCvYrf5U9DMYBECC2uv7YOlr24URVbyCpmYwSQ0&usqp=CAU)

In the picture, the upper line is the _negative_ signal and the lower one is the _positive_ signal. When noise is induced on the _pair_, both traces gain equal induced noise. As a result, the receiver will "see" the same potential difference, and the signal will won't be compromised.

Another thing to note, however, is that the length of the traces must be very similar or signals on both lines won't be exact inverses of each other (one signal will be ahead of the other, in a sense). This is called _scew_, and it is important to minimize this as much as possible when routing differential pairs. For this reason, most EDA applications include a differential pair router that will keep the pair traces are close together as possible in order to match each trace's length. This also keeps the impedance of each trace (usually referred to as Z<sub>odd</sub>) similar, something else that is important.

![trace lengths](https://kicad-info.s3.dualstack.us-west-2.amazonaws.com/optimized/3X/5/1/51f85ddeae6963d809afc331f2af611e1ad6cc05_2_690x374.png)

Length matching is also why some traces have little squigglies since this adds makes the trace a little bit longer. Officially, this is known as serpentine routing.

For its ability to withstand noise, differential pairs are very useful; they are used in USB, which is an incredibly popular communication system, and they are also used in CAN communication, which is used in cars (where there is a lot of noise, as you may expect). 

### Routing

USB 2.0 uses only one differential pair, but USB 3.0 uses 3 differential pairs; 1 pair is a preserved USB 2.0 line (unlike USB 1 to USB 2, the older generation line has a hardware connection from the peripheral to the primary device) and the other pairs are receive and transmit lines for USB 3.0. This creates a slightly frustrating routing issue, since the the seven-port usb hub would have 15 differential pairs to route with required impedance matching. Using a 2 layer board with one layer being a full ground pour, this becomes slightly difficult. I considered switching to a 4-layer stackup that looked like this:

![4 layer](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/4layerboard.png?raw=true)

but that would be almost double the cost. Since I haven't finished the board yet and don't need to anymore, I'm not sure if I would've been successful in only using 2 layers.

This was my ratsnest prior to starting anything:

![ratsnest](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/ratsnest.png?raw=true)

Although my previous boards have looked worse, it is still slightly disheartening when there are so many lines that you struggle to make them out. 

Another thing to consider when designing the board was making sure that the differential impedance matched the USB 2 and 3 specifications. Both require a differential impedance of 90 Ohms throughout the entire line, from device to peripheral, (be careful since USB 3.1 has a range of possible differential impedances), which is the sum of each singular impedance. Essentially:


$ Z_{diff} = 2 * Z_{odd} $


Actually, all the necessary equations can be summed up by this image:

![impedance](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/diffImpedance.png?raw=true)

Since USB 2.0 and USB 3.0 require Z<sub>diff</sub> of 90 Ohms, each odd impedance must be 45 ohms. Using an impedance calculator (kicad has one), finding the correct trace width and pair spacing is incredibly easy:

![kicad calculator](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/diffImpedanceCalculator.png?raw=true)

Although the odd impedance isn't exactly 45 ohms, the error is under the 10% usb tolerance, so it's alright. 

In kicad, if you specify the differential pair gaps and widths in the net class configuration, the differential pair router will automatically use the correct configuration for all pairs. Alternatively, you can configure each differential pair while routing.

There were also a bunch of smaller things to keep track of that I'll list here:

- High speed usb 2.0 allows a 0.6 inch (roughly 1.5 cm) length mismatch between the + / - lines of the DP
- It is still important to keep the pairs away from oscillators and switchers
- Route all corners as two 45&deg; corners or curve them (don't have sharp corners)
- USB 3.0 lenght mismatch should be no more than 3.81mm
- keep changes in trace width as close to external connectors / chips as possible
- TX differential pair on USB 3.0 lines must have 0.01uF capacitors in an 0402 package or smaller and they should be placed as close to the connector as possible

That wraps up the part specifically about USB. Since the project would've also required consideration of the placement of high-current power lines which can also induce noise, I'll go over that here too.

### Magnets Inducing Noise

Current is defined as the change in the magnitude of a charge at a certain place with respect to time. This means that anywhere that charges are moving, there is a current created, and this current will create a surrounding magnetic field on a plane perpendicular to that upon which the charges are moving. In the case of a wire, this means directly up and around:

![wire magnetic field](https://github.com/seanboe/temp_site/blob/master/assets/images/usbhub/magnetics.png?raw=true)

with a magnitude of:

$ B = \frac{u_{0}I}{2 \pi r} $

where _r_ is the distance from a wire.

This magnetic field will induce a current in a wire parallel to it as pointed out by Lenz's Law, which basically says that an induced current will always create a magnetic field that opposes a change in flux. This means that if a wire carrying a perfectly smooth current is parallel to a wire carrying no current, there will be an induced current in the second wire for a short period when the current in the first wire is applied and removed. Since it is unlikely that you could ever achieve such a smooth power line especially when it's supplying motor power (which it was in my case) it is likely that you'd always have an induced current in the parallel wire. This is noise!

The best way to mediate this problem is to place all wires perpendicular to a large current carrying one since magnetic fields can only induce a current in the sections of conductors parallel to them (if a conductor is tilted, for example, then there is theoretically only an induced current in the part perpendicular to the current-carrying wire). This is what my design was going to be based on; a flat pcb with a hole through which a power cable would be placed. This way, as long as no components on the board are too big, the induced noise should be fairly low. Additionally, I planned to place a ferrite ring around the power cable where it'd meet the pcb to act as an additional shield. 


<hr>

## Conclusion

Although I haven't made the usb hub yet and I might never need to do, I still think that learning about it (and thinking that I'd need to make it) was a really valuable experience. I learned what a differential pair was, how it worked, and what it's used in, as well as ways to reduce noise on the lines, which is super useful to know. I also learned how to use some kicad tools that I didn't know about, like the differential pair router and length matching tool, as well as how to use some tools in the calculator. In the process, I also found that [altium's blog](https://resources.altium.com) has really good explanations for lots of different electrical concepts, and I'm sure that I'm going to consult it in the future.

I really hope that I can someday make a board with an integrated usb hub (maybe next year...), but until then, this blog post is here to remind me of everything I learned in case I forget. Hopefully you learned something too!