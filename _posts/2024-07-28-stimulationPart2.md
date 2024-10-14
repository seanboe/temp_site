---
layout: post
current: post
cover: assets/images/stimulationArmStepResponse.png
navigation: True
title: Muscle Stimulator Part 2
categories: [ Biomech, PCBs ]
---

_Forword: I need to thank my lab mentor, [Chris Shallal](https://www.linkedin.com/in/christopher-shallal-4a5634150/), for helping me out on this project, especially on the human-bio side of things. He's the reason I didn't accidentally electrocute myself :D_

After nearly three weeks of waiting (digikey parts came in super late due to a lab financial mixup) everything finally came in. I spent about a day soldering everything with a new metcal soldering iron I bought on eBay and tested it out on the weekend, starting with the flyback converter. I was concerned that this wouldn't work since I designed it pretty hastily and bought a few insanely cheap &#xb1;200V [flyback](https://www.amazon.com/DIANN-Converter-Adjustable-Capacitor-Charging/dp/B0BWN4XNHJ/ref=sr_1_13?crid=2QEGKWMWNX0NG&dib=eyJ2IjoiMSJ9.xu_q7KxCvvL10LmSeyfQLwipaKkC6QKCP6iw3p_LtDvbPyMB84eHRwFbLczu5F9LLrwciCSwoIMZNkUKXF90IfAoXNJB5KJFtahgsZ2thJHLZWNQQWySXb4ZEMTvFyeDGsFK1e6UygJCq9e09Juif5TQbeuNV_8uZK9s0A7UlMd-mFI3xQ3M7VcFo7OOCBTvC5ED0unxU9hviAwz2LB9Kj32u_WHyuo2Cv32Y3rgEME.zhGoewcaxu1DgULXFg4tIhxyOF59cxjqIeHDVmAa7dY&dib_tag=se&keywords=396v+flyback+converter+module+yellow&qid=1722696343&sprefix=396v+flyback+converter+module+yellow%2Caps%2C148&sr=8-13) converters on amazon. Seeing something that cheap and "sus" charge to 350V is pretty crazy: 

![Sketchy Flyback](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/sketchyflyback.png?raw=true)

Have I mentioned that [flyback converters](https://en.wikipedia.org/wiki/Flyback_converter) are really cool? They're inherently isolated (one of the reasons I chose them for this, since IEC 60601 mandates this) so providing feedback to the controller can be tricky. Most chips use optocouplers, but the [LT8304-1](https://www.analog.com/en/products/lt8304.html#part-details) samples the primary-side coil back-EMF. Pretty cool.

# Debugging


## Flyback

For reference, here's the schematic for my flyback (almost a direct copy of one of the application examples):

![Flyback Schematic](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/LT8304FlybackSchematic.png?raw=true)

Initial tests of my flyback converter were a bit shaky. I don't have any pictures of this, but basically the output voltage was much lower than expected - around 20V. Probing the SW pin showed periodic (at a frequency of 1-2Khz or so) ringings of ~2V that would dissipate, rather than roughly rail-to-rail switching, as I expected. The ringing frequency was roughly 40MHz, which was almost certainly my RC snubber (across the primary winding). The DZ snubber was getting hot though, and since it hopefully shouldn't be necessary (1:5 transformer stepping up to 200V, so the SW pin should technically be at about 40V at steady state, giving transients a ~50Vpp margin, and this transformer has low leakage inductance anyway) I took it off. That did the trick. Looking through the documentation again, it became pretty clear that I had just specced this thing wrong. With a 15V input and a 24Vz zener, I was basically clamping at the exact steady-state voltage and (I imagine) not giving the SW pin room to deal with the initial step response in trying to start the regulator. Instead, nearly all that energy was being dissipated in the DZ snubber, leaving almost no energy for the flyback to do any voltage conversion. Hence the 20V, rather than 200V, output. 

![My Flyback](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/myFlyback.png?raw=true)


With ~2.5W input power, maximum output current should be around 10mA (easy math accounting for losses), which corresponds to a SW frequency of roughly 50Khz, based on one of the graphs. The SW pin was at 62KHz, so seems about right.

## Overcurrent Latch

Next up was testing the comparator circuit. It's not very elegant but makes use of some chips I had lying around: 

![Comparator](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/comparator.png?raw=true)

Knowing the sense resistor (the one that sets the driver output current, check my previous post), a current limit can easily be set by changing R2 and R3. It's latching because of U2 (this could actually be a mosfet, but whatevs), and the __OC_SENSE__ is will be an output to the enable pin of the flyback converter to turn the HV off. Although I don't have pictures of it, this worked without any stress. 

## Driver 

This is what really matters. I first decided to try testing it out at around 3mA and 10V, since that should be low enough to get some current flowing through a 2k test load. Nothing happened. Initially, I thought this was a problem with the way I was communicating with the analog switch, which is through a simple 8-bit shift register. After about two hours of debugging (the first half of which I spent discovering that the ground strap on my oscilloscope probe broke and the second half of which I spent using the logic analyzer to make "quick work" of this problem) I concluded that my code had to be correct. As it turned out, this was a pretty simple hardware problem that stemmed from rushing through this design a bit too quickly:

![Switch Ratings](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/HV2201Ratings.png?raw=true)

I had somehow completely ignored the &#xb1;10V margin that the analog signal was supposed to have, aside from 10V being too low to do anything. Although I noticed this when looking for similar analog switches but just forgotten about it when looking at this chip! Since I ultimately aimed to switch 0-200V and hand't paid attention to this, I'd just connected $ V_{PP} $ and $ V_{NN} $ to the HV (200V) rail. Testing at higher voltages - around 40V - yielded so much distortion in the current measurements that it was basically hopeless. So much for testing biphasic current stimulation. 

I spent the next few hours looking for replacement switches, yielding nothing since practically all of those made for high voltage are meant for ultrasound, which doesn't require rail-to-rail operation. The "easiest" solution to this problem would be to supply $ V_{PP} $ and $ V_{NN} $ with the voltages they needed, but this would require two more converters: an isolated ~-10V source, and a ~215V source (which would require another flyback). That sounds disgusting, so instead I ditched the analog switch idea altogether. This new topology is inspired by an H-bridge: 

![New Driver](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/newDriver.png?raw=true)

And honestly, this is way cleaner than the analog switch idea. The switches also had the additional risk of being too slow (the max shift register clock was 20Mhz for roughly 400nS commanded switching time, but even then, it feels sketchy to require a communication protocol at all). There are two mosfets on each quadrant of the H-Bridge so that I can swap test out different ones. They have different footprints. 

# Testing

Although the analog switch wasn't going to work, I could still test the constant current driver. After hooking everything up on a breadboard,

![Switch Setup](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/driverSetup1.png?raw=true)

It worked! The current through the 2k&Omega; load nearly matched what I commanded, and, as expected, the Mosfet $V_{ds}$ exactly followed this drop. I tested it up to 30mA, the design requirement, and it seemed to work flawlessly, with basically a perfect $R^{2}$ value: 

![Measured Values](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/driver1ExperimentalResults.png?raw=true)

That said, during this testing, I quickly noticed a problem. Although I knew the mosfet was going to get hot (max dissipation is $ 0.03 * 117.46 = 3.5W $), I smartly neglected to calculate the actual temperature increase. With a thermal junction-ambient resistance of 125&deg;K / W, this mosfet was cooking, and I suspect that it was getting close to thermal runaway.

I slapped a small heat sink on it, and along with a 12V PC fan, things seemed to reach steady-state, for a current of 0.015mA, at around 40&deg;C. Naturally, the second version of the driver features much larger mosfets (From TO-252 to D-Paks, these are chonkers) for a much lower $ R_{thJC} $ and more surface area for a heat sink. I'm still going to need the heat sink though.

Here's the 40&deg;C steady-state, measured using an overpriced FLIR camera the lab had lying around: 

![Thermal](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/drive1thermalPicture.jpg?raw=true)

## Transients

The next step was to make sure that the risetime of the system was good enough to actually match the timing requirements of the system. I'm ignoring the rise time of the flyback charge because that doesn't change during stimulation, so as I mentioned in the previous post, this was just about tuning the feedback resistor / capacitors in the driver circuit: 

![Driver](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post1/finalDriver.png?raw=true)

Here's what the response looked like (voltage over the load): 

![Initial Rise](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/oscilloscope%20pictures/FlybackPrechargedCircuitPWROnTransientWLowSideSwitchingZoomed.png?raw=true)

At 200uS/Div, this sucks! It takes nearly 400uS (double the negative stimulation period) to reach steady-state. I really should've turned on cursors to measure this, but judging from the graph, it looks like the rise time should be somewhere around... 60uS? The RC loop exists between R18, C16, R20, and $ C_{GS} $ of the [mosfet](https://www.infineon.com/dgdl/Infineon-BSS87-DS-v02_00-EN.pdf?fileId=db3a30433b47825b013b60b6e9436ddb). $ C_{GS} = C_{iss} - C_{rss} $, so $ \tau \approx 500.2k\Omega * 170pF = 84.6\mu S $. Seems about right.

Working with the components I had, I dropped R18 to 30k&Omega; and C16 to 10pF. That got me a nice square: 

![Square](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/oscilloscope%20pictures/DS1Z_QuickPrint3.png?raw=true)

With a stock RC-looking curve and short rise time: 

![New Rise](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/oscilloscope%20pictures/DS1Z_QuickPrint4.png?raw=true)

Finally, just to prove that C16 was necessary to attenuate the transient, I removed it. This means that the transient response is much more dependent on the op-amp characteristics, since we're basically just testing the negative feedback speed (which is dependent on slew rate, maximum output current, etc.) The OPA810 is pretty expensive, so let's see how it performs: 

![No Cap](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/oscilloscope%20pictures/DS1Z_QuickPrint7.png?raw=true)

Whadaya know! I'd rather not have 40Vpp transients... the cap is going back on. 

After a night and day grinding, I sent out new boards (the ones with the H-Bridge configuration) with the confidence that the driver, at least, would work. Here's what the cad looks like: 

![New Cad](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/newDriverCad.png?raw=true)

## Stimulation

The day after everything got sent out, I realized that I hand't even stimulated myself yet. Although I wouldn't be able to have charge balance, DC stimulation can be used for short periods safely. I hooked up some electrodes to my forearm, stuck them in the path of the load, and started off with 2mA of stimulation. Needless to say, it worked! muscle stimulation without contraction feels really weird... it's as though your muscle is vibrating really quickly, but a little... pokier than that? It's hard to describe. The good part of this test is that it felt just like the [expensive stimulator](https://www.digitimer.com/product/human-neurophysiology/peripheral-stimulators/ds5-isolated-bipolar-constant-current-stimulator/) we have, so it seems like things are looking good. 

I obviously had to capture the stimulation transient (which is also the cover of this post): 

![Sean Arm](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/oscilloscope%20pictures/SeanArmStimulation.png?raw=true)

The rise is a function of my muscle impedance. Theoretically, I should be able to do a frequency sweep over my muscle to come up with a circuit model for it, (there's a picture of this in my previous post, although the paper that discusses it doesn't really explain how they got their values) but I'm not going to do that until the biphasic stuff is working. I'm not trying to cook my arm here. 