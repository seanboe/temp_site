---
layout: post
current: post
cover: assets/images/impedance-learnings-hero.png
navigation: True
title: Summer learnings
date: 2022-7-22  10:19:00
class: post-template
subclass: 'post'
author: sean
---

Just a recap of some things I've been studying.

For fun, I've been studying AC circuits since it's the natural subject after DC circuits, which I studied for AP Physics C. This is a simple explanation of what I've learned to act as backup when I forget it...

### What is AC?

AC stands for alternating current. This describes a current that varies between some negative and positive voltage periodically, which is where it differs from DC (direct current). AC circuits are cool to analyze because they result in interesting responses from seemingly simple passive components (resistors, inductors, and capacitors).

### The Passives

The passive components - resistors, capacitors, and inductors are the building blocks of most circuits. Here's a recap of what they do and their characteristics.

__Resistors__ resist current flow usually with a slightly insulating medium. Since the resistance of a resistor is independent of the current flowing through it or the voltage drop across it, resistors maintain constant resistance regardless of whether a circuit is AC or DC. 

__Capacitors__ store electrical energy in the form of an electric field between two parallel plates (which is actually a very thin, flat coil of conductive wire seperated by a dielectric in most cases). Since current cannot literally flow through a capacitor (current flowing through a capacitor is called _displacement current_ while current literally flowing through a conductor is called _conduction current_), capacitors are considered analogous to potential energy in mechanical systems. Thus, when a potential difference is applied across a capacitor, it takes time to "charge up". In the case of DC systems, this is rather trivial, however in AC circuits, capacitors are rapidly charged and discharged, and thus their response becomes important to the average signal. 

![capacitor](https://media.discordapp.net/attachments/881969144814256200/1000130378679472258/rc-rc2.gif)

__Inductors__ store energy in the form of a magentic field in a coil. It works on the principle of self inductance, which is an example of Lenz's law. Whenever current flowing through an inductor changes, another current will be induced by the magnetic field to oppose the change. In other words, inductors are resistant to changes in current, not electric potential, like capacitors. This makes the response of inductors to varying currents almost the opposite of capacitors. Also, since the energy stored in inductors _is flowing literally_, inductors are analogous to kinetic energy in mechanical systems. 

![inductor](https://media.discordapp.net/attachments/881969144814256200/1000133149285683231/unknown.png)

### Passives in AC

Now it's time to put this together in AC. The key differences between the three components can be described by one quality that the three (although indirectly) share: resistance. Allow me to explain.

Resistors have constant resistance in DC and AC - thus, in AC circuits they act no different than in DC circuits. Easy!

Things get a little more tricky with inductors and capacitors, however. Although neither have traditional, DC resistance, their delayed responses to changes in potential (which is intrinsic to the AC circuits) can be likened to variable resistances. 

Let's look at inductors first. Assuming that the AC input is sinusoidal, instantaneous voltage can be quatified as such:

<html>
<center>

\(\Delta v = \Delta {V}_{max}\sin(wt)\)

<br>

<p> Assuming that there's only an inductor in our AC circuit, the voltage on the inductor equals the AC voltage:</p>

\(L\frac{\mathrm{d}i}{\mathrm{d}t} = \Delta {V}_{max}\sin(wt)\)

<p>Solve for i (instantaneous current)</p>

\(i_{L} = \frac{\Delta V_{max} \sin(wt - \frac{\pi}{2})}{wL}\)

<p>This expression becomes analogous to Ohm's law, where resistance <i>R</i> equals <i>Lw</i>. This is known as <i>inductive reactance</i></p>

\(X_{L} = wL\)

</center>
</html>

Concisely put, inductive reactance is resistance of an inductor for an AC system. The important differentiator between _resistance_ and _reactance_ is that reactance is _frequency dependent_ - the AC frequency changes the "AC resistance" (reactance) of the inductor. Note that the reactance of an inductor is proportional to the frequency of the voltage applied to it.

For capacitors, there is an inversely proportional relationship between reactance and AC frequency (I'll save you from the derivation):

<html>
<center>

\(X_{C} = \frac{1}{wC}\)

</center>
</html>

Thus, it can be seen that the reaction from capacitors and inductors in AC circuits is opposite. This makes sense when analyzing a single AC pulse. When the voltage increases on the pulse, the voltage across an inductor will immediately express the applied voltage (as a result of the reactance), but the current will slowly increase (also a result of the reactance). Meanwhile, a capacitor will take a while to express the applied voltage, but maximum current will flow through it immediately. 

Altogether, the sum of the resistance and the reactance of a circuit is called _impedance_. Doesn't that word sound cool?

![impedance](https://media.discordapp.net/attachments/881969144814256200/1000162236809085011/Screen_Shot_2022-07-22_at_3.07.33_PM.png)

### The importance of impedance

Although there are many more reasons to care about impedance, impedance matching for high speed lines is the most clear to me. For differential pairs, for example, it is important that the inverse response is as precise as possible. If impedances aren't matched and the environment's effect on the individual impedances isn't considered, it is possible that the signal is attenuated or distorted relative to the other line. This violates the very principle that differential pairs try to preserve and it's why differential pair routing is so important.

### More applications

Since inductors and capacitors have reactance (which is frequency dependent, as I already pointed out) they can be useful for doing passive AC circuit / noise analysis. This is the main application of filters. Take this system, for example:

![low pass filter](https://media.discordapp.net/attachments/881969144814256200/1000160774959927307/fil5.gif)

For a low AC frequency, the reactance of the capacitor is very high (since capacitive reactance is inversely proportional to frequency), which means that the ratio of the capacitive reactance to the resistance is very large (relatively speaking). Thus:

<html>
<center>

\(\frac{X_{L}}{R} > 1\)

<br>
<br>

\(\Delta V_{C} = \Delta V_{out} > \Delta V_{R}\)

</center>
</html>

On the other hand, with high frequency, the voltage across the capacitor will be less than the capacitor across the resistor. In essence, it acts as a variable voltage divider dependent on frequency, but also has a really interesting relationship. High frequencies are atenuated very strongly whereas low frequencies aren't:

![low pass filter graph](https://media.discordapp.net/attachments/881969144814256200/1000164490496708628/unknown.png)

This is called a low pass filter!

If you measure across the resistor instead, you have a high-pass filter (since the opposite happens). Meanwhile, if you replace the inductor with a capacitor, then the configuration of the filter and the filter type are flipped (since it is opposite again).

Cool, right?


### Root Mean Squared

Switching topics; time for Root Mean Squared (RMS) Voltage. There are a few ways that you can measure voltage:
- Peak voltage (for AC, this is the amplitude of the voltage signal)
- Peak-to-Peak voltage (this is double the amplitude)
- Average voltage (exactly what you think it is)
- RMS voltage (you'll see...)

For AC, the first three have some problems:

- Peak voltage isn't so useful since it is... the peak voltage. For AC, the voltage is only peaked for a short time! This isn't accurate.
- Peak-to-Peak voltage suffers from the same voltage as peak voltage
- For AC, average voltage is always 0, since the period above 0V equals the period below zero volts. One might say that this isn't a problem just looking at (ideal) inductors and capacitors, which will dissipate all their energy back into the voltage source. The issue is that resistors will not - part of the current passing through them will be converted to internal energy in the form of heat. Thus, using V = 0 isn't convenient - it makes a lot more sense to find a voltage value that is useful in computing energy losses. 

This is where RMS voltage comes in. It is the AC voltage squared, taken the average of, and then square rooted - basically, the average of the absolute value of the AC voltage sinewave. RMS voltage is the AC voltage applied to a resistor to result in the same energy losses as a DC system with the same resistor. Since an AC system with amplitudes equal to the DC voltage source of another system will not always be at its peak, it makes sense that RMS voltage is always greater than DC voltage for resistor power consumption to be equal. Specifically:

<html>
<center>

\(\Delta V_{RMS} = \frac{V_{DC}}{\sqrt{2}}\)

</center>
</html>

Ok, that's all for now! Later I'll also post on what I've learned on resonance and damped oscillations in circuits.