---
layout: post
current: post
cover: assets/images/stimulator/post3/stimulationWaveform.png
navigation: True
title: Muscle Stimulator Part 3
categories: [ Biomech, PCBs ]
---

A week after sending version 2 of the driver board out (see my previous post) everything came in. I soldered it all up, and I was once again impressed by how close the 3d model in kicad got to reality:

>Forword: I need to thank my lab mentor, [Chris Shallal](https://www.linkedin.com/in/christopher-shallal-4a5634150/), for helping me out on this project, especially on the human-bio side of things. He's the reason I didn't accidentally electrocute myself :D

The 3d model:
![DriverV2 model](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post2/newDriverCad.png?raw=true)

The actual board (it's a bad picture, but trust me, they look identical)
![Reality](https://github.com/seanboe/temp_site/blob/master/assets/images/stimulator/post3/driverV2PCB.png?raw=true)


I replaced the [old stimulator](http://localhost:4000/blog/stimulationPart2/) with it and soldered up a new flyback converter set to around 130V. I'd used 180V previously, but after a few nasty shocks (which I decided to omit mentioning in my previous posts...) it seemed a bit high. My muscle impedance isn't that high and I'm not stimulating much current. The most I'd tried was around 3mA on my forearm. 

I stuck a $ 2k \Omega $ load on it, and the setup ended up looking like this: 

_insert image_ 























This was super exciting. I let a few other people in the lab try it, and we were even able to get someone's thumb to contract. Later, I did it myself and filmed it:

<iframe width="560" height="315" src="https://www.youtube.com/embed/6Ep7u_Obvww?si=Tw4OjFrqbyPo8Os9" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

I realize that it's super easy to fake this, but hopefully these posts give you some confidence that it actually works...

It was now time to test multichannel stimulation, the idea being to multiplex the stimulation waveform on multiple loads using solid state relays. For the past year, we've basically been using a [board](http://localhost:4000/blog/biomech_1/) dedicated to this for patient testing to multiplex the FES out of a DS5 stimulator. 

Along with version 2 of the driver, I sent out a small board to test this on two channels:

_instert image_

_insert image_

As before, I soldered a $ 2k\Omega $ load on both channels. At first it only worked on one, but eventually I realized that I flipped both relays on one of the channels. After that, it seemed like the coast was clear, but instead I started measuring this weird distortion with some clear transients getting through the channel that was off. I was pretty confused at first, but then realized that it was just a result of the output capacitance of the relays. The initial impulse, which is a super high $ \frac{dV}{dt} $, just passes straight through because of this capacitance.  

The second source of confusion for me was what appeared to be a slight time mismatch (around $ 100 \muS $ maybe?) between both halves of the stimulation waveforms. I couldn't totally figure this out, but since the relays weren't matched (and their on-time is on the order of 100s of microseconds) it's probably just a result of manufacturing deviation. 