---
layout: post
current: post
cover: assets/images/OpenServo/Post2/heroImage.png
navigation: True
title: Debugginggg
categories: [ OpenServo ]
---

And so the problems come rolling in...

Here's another quick update on the openServo project. I've run into some problems and been able to fix a few, but there's still a lot of work to be done!

Firstly, after doing some more testing with the encoder, I discovered that there is a 5-degree deadband at the 355-0 degree range. Basically, between those points, the encoder won't read anything, which means no accurate shaft positioning between that range. It's even more annoying that its right at the position where the shaft would make a full rotation, since it then becomes very difficult to determine when the shaft has actually passed 360 degrees and made a full rotation. I really should've seen that the deadband exists in the datasheet, but in my defense, it was listed in a really small corner of the 40-page datasheet... still, I should've probably read it. 

Anyway, I have found a solution other than purchasing a more expensive verison of the chip with higher resolution - the [AS5048B](https://www.mouser.co.uk/datasheet/2/588/AS5048_DS000298_4_00-2324531.pdf), which is popularly used with Odrive. It's actually really simple; the idea is to recognize when the shaft is about to enter the deadband region (either 355 or 0 degrees) and then to interpolate across the deadband, which is a known distance. In order to determine the time, simply calculate the angular velocity - this is something that I need for seperate analysis anyway. When the shaft enters the deadband region, instead of updating the position from the encoder, update from the interpolation, and then when the interpolation is finished, the shaft will have just escaped the deadband region (as long as it continued on the predicted path, meaning no large resistive forces). 

The direction of the shaft through the deadband region can easily be determined by looking at the sign of the velocity immediately prior to entering the deadband region. Depending on this direction, the total number of full rotations will either be incremented or decremented.

> Remember, magnetic encoders measure absolute position, not incremental position! This is why the number of full rotations must be incremented manually.

Here's the code - note that I used the [Ramp.h](https://github.com/siteswapjuggler/RAMP/blob/master/src/Ramp.h) library for interpolation and the `velocity` object is a custom class object used simply to calculate the rate of change between two points.

``` cpp
void ShaftAnalyzer::update() {

  if (!inDeadband) {

    if (getEncoderReading() > (DB_START - DB_THRESH) && getEncoderReading() < DB_START && millis() - dbUpdateTime > DB_BUFFER_TIME && abs(velocity.getVelocity()) > 0) {
      inDeadband = true;  
      dbUpdateTime = millis();

      dbRamper.go(DB_START + (fullRotations) * 360);
      fullRotations++;
      dbRamper.go(fullRotations * 360 + DB_THRESH, abs(DB_DISTANCE / velocity.getVelocityMillis()), LINEAR, ONCEFORWARD);

    }
    else if (getEncoderReading() < DB_THRESH && millis() - dbUpdateTime > DB_BUFFER_TIME && abs(velocity.getVelocity()) > 0) {
      inDeadband = true;  
      dbUpdateTime = millis();

      dbRamper.go(fullRotations * 360);
      fullRotations--;
      dbRamper.go(fullRotations * 360 + DB_START - DB_THRESH, abs(DB_DISTANCE / velocity.getVelocityMillis()), LINEAR, ONCEFORWARD);
 
    }
    else {
      currentPosition = getEncoderReading() + 360 * fullRotations;
    }

  }
  else if (inDeadband) {
    currentPosition = dbRamper.update();

    if (dbRamper.getCompletion() == 100) {
      inDeadband = false;
      dbUpdateTime = millis();
    }
  }

  if (millis() - velUpdateTime > VEL_BUFFER_TIME) {
    velocity.calcVelocity(currentPosition);
    velUpdateTime = millis();
  }

}
```

It's really simple! 

This solution has a few pros and a few cons, however.

Pros:
1. Super simple, and easy to maintain - it also works in the negative direction
2. The velocity can still easily be calculated on top of the position (without weird conditions on the shaft, transitions are seamless)

Cons:
1. The interplation is linear and won't adapt to the acceleration of the shaft immediately prior to it entering the deadband. This is OK for two reasons, despite still being a con: first, the deadband region is fairly small, so a linear prediction shouldn't make a big difference (this is a similar idea to a derivative, conceptually), and secondly, accelerations / forces applied to the shaft immediately prior to entering the region will likely take it off path anyway, making the prediction a bad one regardless of this being considered
2. It still isn't that good since no position in the deadband can be used as a setpoint or reference position. 

Either way, I'm still pretty happy that I got the AS5600 (the current encoder that I'm using) working, since it's less than a third of the price of the one with higher resolution. Other than the region in which it has a deadband, the encoder is also remarkably accurate and out does many of the accuracy requirements for this project. 

Another problem that I'm running into has to do with controlling motor torque. Currently, the way the motor velocity is being controlled is using a Pulse Width Modulation (PWM) signal. For every time step (determined by a default frequency) a pin will read high for some period of time and low for the rest of the time. The proportion of that period of time to the total time is called a _duty cycle_.

![image](https://cdn.shopify.com/s/files/1/0615/2193/files/duty_cycle_large.jpg?v=1579814273)
*Notice how the period is independent of the duty cycle*

Effectively, the voltage is averaged between the on and off states, so the effective voltage is proportional to the duty cycle. 

The PWM signal that is sent by the processor is amplified by an H-Bridge circuit inside the [TB67H450](https://toshiba.semicon-storage.com/us/semiconductor/product/motor-driver-ics/brushed-dc-motor-driver-ics/detail.TB67H450FNG.html). H-bridges are super simple switching circuits that allow you to control a dc motor at much higher currents than your signal lines:

![H-bridge](http://modularcircuits.com/blog/wp-content/uploads/2011/10/image7.png)

By turning on and off mosfets on opposite sides, you can cause the motor to turn different ways. There are more configurations that are shown in the datasheet of the TB67H450.

![more](https://media.discordapp.net/attachments/920561717841371226/991915731006521384/Screen_Shot_2022-06-29_at_8.58.53_PM.png?width=475&height=569)

It's really simple, but still really cool!

Anyway, back to the PWM. By using PWM to control the H-Bridge signals, the voltage driving the motor is averaged in the same way that the signal is.

Time to switch concepts a little... I'll get back to that PWM stuff later. Firstly, the current draw by a motor is proportional to its output torque, so maximizing the current draw by the motor will maximize it's output torque.

One more thing: Ohm's law shows that 

<html>
\(V=IR\) &#8756; \(I = \frac{V}{R}\)
</html>

Now everything comes together: the PWM signal is lowering the average voltage, which is lowering the output current of the motor (note that the motor's internal resistance is constant, on average), which lowering the output torque. This is really annoying since I can only control the torque by varying the PWM signal, which varies the velocity; the velocity is proportional to the output torque. As a result, the stopping position of the motor is before the point at which the duty cycle is 0 since the torque becomes too low to push through the gear box (I know, right?? 😭) which results in a latency in moving the motor. This was easily apparent during positional control of the motor (which is working by the way, and is still really cool! - next post).

Here, the red line is the setpoint position of the motor shaft and the orange position is the actual shaft position. You can see that as the motor gets really close to the end of the path, it overshoots and begins moving back to the command position in a very step-like motion. This is because the motor's torque is so low that the PID controller overshoots and doesn't know how to control it.

<br>

<iframe src="https://giphy.com/embed/qcUXtCikx8wp2eHqgq" width="600" height="354" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>

<br>



So what is the solution to this?

Well, my plan is to compensate for the reduced current by increasing the applied voltage on the motor to above nominal voltage as the duty cycle decreases. This way, the average voltage can be maintained while duty cycle changes - note the difference between instantaneous and applied voltage. Also, DC motors break due to high currents, not high voltages (although this can _result_ in high currents), so this plan won't put the motor in any danger, even if the instantanous voltage is well above the rated voltage of the motor - the rated voltage is the average voltage, in this case. 

> Motors break due to high currents because the high current will lead to heat dissipation that can destroy the thin insulation surrounding the copper wire in the motor's coils.

Additionally, this plan allows me to control the motor's velocity _and_ torque directly; all I need to do is figure out the relationship between duty cycle + applied voltage and torque output, and duty cycle + applied voltage and velocity. It's a little confusing, but in a few weeks I'll have a new board designed and will have hopefully ran a couple more tests (the tests I've done prove the concept, but are still a little primitive). 

This new idea will require some changes to the existing board, namely the addition of a boost or buck converter to control the applied voltage on the motor. I hope to build my own circuit for this since they are fairly simple and don't require too many components; here is a sample schematic for a boost converter, which I'm leaning towards using:


![boost converter](https://github.com/seanboe/temp_site/blob/master/assets/images/OpenServo/Post2/boostconverter.png?raw=true)

Hopefully this will work! Currently, my only fear is that there won't be enough space on the PCB for this to be integrated - maybe I'll end up using an IC if it's compact enough.

That's all for now!