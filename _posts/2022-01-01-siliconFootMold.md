---
layout: post
current: post
cover: assets/images/quadruped_pics/feet/caulking_first_try.png
title: Silicon Foot Mold
categories: [ Quadruped ]
---


During winter break, I did some experimenting with using silicon as a material for making feet for my quadrupedal robot. As one might expect, making good contact with the ground is important while walking, for all species. It's why we wear shoes... that, and so that we don't hurt our feet on rocks and stuff. 

Since the beginning of this project, I'd been doing research on ways to make suitable feet for my quadruped, and went through many iterations. First, the ordinary 3d-printed plastic foot. This didn't work at all, since it was so slippery. I knew that I needed something slightly grippy, so I also experimented with using foam nerf balls rival as soles for the plastic feet and as feet themselves. They were the perfect size and are also quite grippy - they seem to be coated in a slightly oily/dry liquid, which prevents them from slipping easily. Although this was promising, the feet wouldn't stay on the quadruped's legs since the foam was too weak. Despite many attempts at fashioning a coupler-type attachment that could interface the two parts, I was unable to make this approach successful. 

![Old feet](assets/images/quadruped_pics/feet/foot_attempts.png)

As this expedition continued, I began looking at ways that other people had overcome this problem. Many spot micro builders - a popular 3d printed quadrupedal robot project among hobbyists - used flexible filaments to make a sole-like attachement for their quadrupedal legs. While this may seem effective, it in fact is not. Flexible filaments like TPU are not at all grippy; being flexible has little, if anything, to do with a material's friction with other surfaces. Thus, I saw many spot micro builders suffering from the same problem I was. 

Higher-scale robots, like Spot from Boston Dynamics or ANYmal from ANYbotics (but it was also designed with ETH Zurich) appear to use custom rubber feet. MIT mini cheetah, however, actually uses squash balls with a special inner fitting inside, according to Ben Katz's (one of the main designers of mini cheetah) thesis. While this marvel of resourcefulness is definitely neat, squash balls are much larger than what I actually need; my original 3d model called for a foot 20mm in diameter, but most squash balls are double that.

![spot mini feet](assets/images/quadruped_pics/feet/spotmini_feet.png)
_<figure>Spot's feet</figure>_
<br>

![anymal's feet](assets/images/quadruped_pics/feet/anymal_feet.png)
_<figure>ANYmal's feet</figure>_
<br>

![mit cheetah feet](assets/images/quadruped_pics/feet/mitcheetah_foot.png)
_<figure>Mini Cheetah's feet</figure>_
<br>

Then, everything changed, after I came across James Bruton using Silicon Gel as his quadruped's feet in one of his videos. While I'd always known it could be done, I thought it would be too expensive and difficult, so I didn't research it much. While part of this was true - silicon gel _is_ quite expensive - it turned out to be easy to use. After a little more research, I decided to try using silicon caulking - which is much cheaper - instead. First I tried making proto-putty with it, which is just a mix a silicon caulking and corn starch. This becomes a slightly sticky play-doh like substance that hardens quite rapidly (within a few hours). My first tests (meant only to get a better understanding of the material) came out looking like this (the scratches were created by me with sandpaper in an attempt to make it slightly more grippy):

![proto putty test](assets/images/quadruped_pics/feet/protoputty_test.png)

It's red as a result of red food coloring. Coincidentally, it looks exactly like a pink eraser, and feels just like one too! The material is just slightly more smooth, smells heavily of vinegar, and cannot erase. Unfortunately, I felt that it wasn't grippy enough, however I decided still to design a mold for the silicon and to actually build a real foot. This is the mold I desgined:

<iframe src="https://gmail652231.autodesk360.com/shares/public/SH35dfcQT936092f0e43f5345996027ec752?mode=embed" width="800" height="600" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"  frameborder="0"></iframe>

As you can see, it consists of four parts: two mold shells, an implanted part (meant to interface between the weak caulking and the quadruped's foot) and a holder for that part while the part dries (this eventually ended up not being necessary). The spherical cavern is 25mm in diameter. 

After 3d printing this, I gave it my first attempt, which yielded this: 

![first try](assets/images/quadruped_pics/feet/caulking_first_try.png)

... slightly ugly, yet promising. Ufortunately, it did not satisfy my expectations; not grippy enough. The best why I can describe this material's grippiness is by describing it as having a very similar feeling as a spinach leaf when rubbed lightly, although still more smooth. I decided then to try using pure silicon caulking, which yielded this:

![caulking only attempt one](assets/images/quadruped_pics/feet/caulking_only_1.png)

Why is it still stuck in the mold, you ask? Well, because it was too sticky for me to get out! Also, the inner parts of the sphere were still wet after 3 days, so attempting to yank out the "foot" from the mold wouldn't have worked. 

So that's where I am with this side of the project! If there's one thing I've accomplished so far, it's to give my quadrupedal robot stinky feet... 🤪

I believe that the only-caulking idea still holds promise; soon, I'll try optimizing the shape of the foot (maybe only coating a plastic foot in caulking) to make this idea work. 

That's all for now!