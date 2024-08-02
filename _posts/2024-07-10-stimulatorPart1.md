---
layout: post
current: post
cover: assets/images/stimulationHBridge.png
navigation: True
title: Muscle Stimulator Part 1
categories: [ Biomech ]
---

This summer, my main goal is figuring out how to make a mobile muscle stimulator with "blanking" capabilities. Here's roughly how I arrived at this project:

1. Our lab is inventing [super cool surgeries](https://www.media.mit.edu/publications/mechanoneural-interfaces-for-bionic-integration/) that allow us to provide feedback to amputees via controlled muscle contractions within their limb.
2. A lot of research has gone into neural prosthesis control, which uses electromyography (EMG). Those control schemes are based on measuring a the natural voltage across your muscle during contraction. Won't stimulation mess that up, since you're basically injecting charge? (_Answer: Yes_)
3. We have an awesome _portable_ [sEMG platform](https://dspace.mit.edu/handle/1721.1/124074) that we can use for testing our patients' walking capabilities. Is it even rated for stimulation voltages? (_Answer: No_).
4. Is the [stimulator](https://www.digitimer.com/product/human-neurophysiology/peripheral-stimulators/ds5-isolated-bipolar-constant-current-stimulator/) that we have (the only one that's FDA approved for research) portable? (_Answer: No_)
5. Do we want our patients to have a tether attached to them for stimulation only? Am I concerned about the integrity of the stimulation waveform (stimulation is roughly a 1Mhz biphasic squarewave) if we do this? (_Answers: No, Yes_)
6. We should make a mobile muscle stimulator.

That's basically the gist. The goal is to design a small multichannel (I'm currently aiming for 8 channels) muscle stimulator that can act as a "hat" for the sEMG board in order to be able to allow us to sense (via EMG) and stimulate a muscle at the same time. Why would you want that? Well, I talk about it a bit in my [switcher board post](https://seanboe.github.io/temp_site/biomech_1/), but the main idea is for the prosthesis to be able to relay forces / pressure against it to the amputee by inducing force / pressure on the muscles that would be feeling that. When a leg prosthesis hits something, for example, most users will feel the resulting forces in their hip (since they don't have a leg anymore). The AMI surgery preserves the muscles in their leg and allows us to stimulate them so that users can "feel" that hit. The "sensing" part of the story comes back in when considering how the prosthesis is controlled - using EMG. This relies on measuring the voltage across the muscle the user preserves in the AMI to drive the prosthetic leg in the first case. Since that runs on a tight sampling frequency (I'll go into why this important a bit later) it's a bit tricky to get the stimulation, which charges your muscle, to work with EMG, which aims to measure natural charge buildup rather than the artificial stimulation charge. This makes filtering stimulation artifacts / noise out of the EMG a core technical goal for this project. I'll get more into it later. 


# Stimulator Design

This is what the stimulation waveform is supposed to look like: 

<figure style="text-align: center">
  <img src="https://lh3.googleusercontent.com/pw/AP1GczMQzjfl2YKUAc5aXq8IB_8YQ_escyDoaGQxvOA0_J1aNCidhd15J3uVAVpCwjgtqFsueBv1tyUJKkBxyzjxaj9iirtgao_WBcPj5OFyED7QcY2t9YZLfaETlYjVelr8r8H4NSdy__dvW3RRV1vFxGZ2x0JOQLhlP53ADPgVsiRdq3_-5VSJIvG36xOs6Uin5ATuoLeKmb0F7ISyLNZ2myZZqAA_d4sQNW8VPxEt_AKfFh2xMcSHW5TgSMNQqIC0xr8ADsoOkas7CCXdhbRtZOiCk_hXdUtw3D0eRpUe_ze3Nbi5Uqh0Zfq08NVmBvYvebJkLtWcX-I0ORHGE-9IUsIZxLWwGM7nl3b1S59_uNQhvNgnZaF6YudmzPgHlo2paNWjHHAt30yD8e47lOkuP-tRB7r5Seq3qez754IHubNNHoIMpT6i_8Jsi3z0ELxCiuBhmR56dbDT0E-4pbohPQcxAbaP4Bi2N_Mz3VuGwYRpHWOTXpWcr1-3XtpfC6WLMLNPn0AEHIUBLdgxDFC3QYf890JodbVUgOQkYH_Q7x1aOLZpOYHNqiekRwb2HD6Go2MXyeS8asGXVJrbnIc4k1RaKRvKvTm7bOgzQwYlK2IvbZYJIvKSnvu1-1M1Vo_AE-0EN7R5GXXOvpQlAtqyuwU6mPIqWV59tjNnmiGKWUZc1colqamzcy8I8IExbYjYlneovi9uN1cvEhd8kJ54iww9jyVcFkDsOzz5oJ-zm1aIaRjWrMwLt52sSYA2Tp31oZX3lJ9o-HXD4-OCcbtPiqVNg9zNZI-FZN5dUXkuPROKxWMnXO0rVwbcncYZaxXp-7Z5lw1BBi_DUl9z6O7VMRKRHMVPbVwPemBOIKLaBjXqCsAD54AancmyJMdh1yCSoI5qbplM95eYJYcHQKavPSikoNYbj8rVQxtL9joyZl7QZVl7FJk8fiLs8dCeTQ=w708-h302-s-no?authuser=0" alt="my alt text"/>
  <figcaption>From: <a href="https://jneuroengrehab.biomedcentral.com/articles/10.1186/s12984-018-0474-8">Safety of long-term electrical peripheral nerve stimulation: review of the state of the art</a></figcaption>
</figure>

It's biphasic because it stimulates both positive and negative current, and asymmetric because the magnitudes of each are different. 

I also forgot to mention that contraction amount is a function of the charge injected in the muscle. As of now, the most charge that can be used to stimulate for research (as regulated by the FDA) is 30mC I believe. That's what makes the biphasic aspect of this good, since we can maintain net zero charge in the muscle by making the integral across a waveform period 0, and why we need current control, as opposed to voltage control. Charge inbalance can lead to fatigue and skin rashes. 

For us, the stimulation parameters are roughly:
- D: 200uS
- W: 100uS
- The unlabled positive time period: 2mS
- _f_: ~500Hz. 

Not too bad. 

The actual stimulation current depends a bit on the person, but in the average muscle, vibration / feeling occurs around 1mA, and contraction occurs around 10mA with this waveform. Things start to hurt past 15mA, and damage starts to occur at 30mA. That said, patients sometimes have completely different responses (some start to feel vibration at 10mA).

## Research:

I started off reading a few (actually it was a bunch, but as usual, only a few were actually helpful) papers on stimulators to see what current circuits existed for this kind of stuff. Muscles are typically modeled as a bulk resistor in series with a parallel resistor / capacitor arrangement: 

<figure style="text-align: center">
  <img src="https://lh3.googleusercontent.com/pw/AP1GczP5AdlugAAh6Pqcc3YO0IiiTU3Vrf-iZ8_AH27c1JSdLySnLwbADLRzxYlKeDlPR0Q-cvG9ocAV0nsnmuby3fdT0XfydcNCP_bPxlNBOVbxOut76uRjPijdVur1gIU8ya8aS4D0NOIZ8QDM2OPaBH-8UldbeSaKFxkBp1bdO0WMWntFPCFsHxeWlHZp__KZamabr9lbJWPfr5Wq99AiTe0PoT92qgbaJxKjclZAQjzumGzIvMgODXtDNzjK_3aRa5Z-ju9FrJzsl4waLVkm3seajugQJ7P3VdFbOeeDrK0axhv7ekMY7LLrEpNcmMFhh0a-Pm7_D_jsZ2wwrKeV1pkGAbT8vmf4mweIKxTSFYr7JTKBQbiJMEsEWGBicKCmKCoIfkJ5SNn-bjMZlzGEa1TJo5idD9vDKxFfVqzhAZpdj_FPvEMj4LD5naL0WRu2Zi5EVGRalOFZrbJ4BRIzAsPKTTwkC4Xye6NSOI5JJlPZDW819bKhLw-eoMuhiU2xzB5149D7h7s9aeIB4wuBtZ2s1w7N6WeY32VyBgmkM3oLDVdb4vAY_uNRkJ84eQZlSisY7is8zmH9yoG4yiCXF9fnjYHIInKa8vdyqBVetbw_lade7LzX91cLUicUUe58qM77qu-1PsAbdSkoUieR5m4fEUnOU6W6c0HQwofcg8Mr0FRho78V0LIWLGdS-rzSSoLCppL2p70CvpcWQ-kfwnyi90bGaQcQ-F2JJeXZf2X2BAFUxCLh5esqhTo5mbFwMUu7agam0fxDIZQneRv1Ccj-v3ue-AQZi29bLJQzGK5Y4qdpkOaQuLdP0TAh8L1zUxCneOQAWIOgrHpqhg-rCx1hfAVKmNITuBlRf2Pm42Yho4MLf7QIlBUb6ww8aeUpDWhLlxi9quxkkpPhmqUoLOm44NdEUsdbMmMq4QTp_b_3DJQ5vFvgqunSqYw-Qg=w913-h400-s-no?authuser=0" alt="my alt text"/>
  <figcaption>From: <a href="https://ieeexplore.ieee.org/document/775402">A High Voltage, Constant Current Stimulator for Electrocutaneous Stimulation Through Small Electrodes</a></figcaption>
</figure>

In practice, we've found Rs to be accurate, and Rp to range from very low to around 2k&Omega; as well. This means that at a maximum stimulation of 30mA, a maximum muscle resistance of 4k&Omega; would require... a 120V drop! Keep that in mind as you look at these designs. 

Most stimulators I found in literature were constant voltage controllers (again, bad because the current / charge then depends on the muscle impedance). These are some of the more promising current controllers I found... and why I didn't like them: 

<figure style="text-align: center">
  <img src="https://lh3.googleusercontent.com/pw/AP1GczNgtg3eg37hhIRGSNX1_Qt6X5FZn9EzTq7_N8d5UWD-lht2AC7qXwu_qe7mxKXQ0rfoik0nz6cmj0x4R7WX2utjcvFgRyAQdhv1AbGx1HtkKKJBbrv_v6GGGDVfsXo2LAUFHXddnncKHK17_ZYKMbFApfeVSFgsuLgs-8RUhzqy--vCXkSGis2Vpr5lVsC38Jg58txcy2GV2kppV-dRxoHcHWvJCqNjM0l7AD6ppiF7YGIb7iJRjNwdoNW2Z3a0lqLus9bStuU4F7kMBZDbTrFMlJlTYxMXhH0Kqr-JklKcfqpFPm62vEQY0RqyWbytgMkN2vEGIdvmoDOqhp4PLqhdLATekgDwFTEUJQYFGXVgTz_y4ihaqF3W8beEp633RPxzeHqcrryjXSKptoSo0CMcMkGR08z4Qz3Z_xEHFHVeVDm3WiQyJJNk--GWRFlkxS86Y-q00F97XMn2vx2jghDQ9fj6h3Ww_Z94uBI984rQcb5NNFHwdxmjuMLX8UJ8uzvdu-blGTfeivGS-BUPyDOTTvlcSKyc9smmyeXGXj3wjTvGJCmorS6loHvybathYDSmjoUtFQ76mv1uxMrDslzPH4fQaLsBJEMBUZiI_u9J6iB-wSK0KNNgf8rUFs-mCrLDeprI4b48SzfanSIrkLDRkspl76ekxKw1xyq9k_QnIAy5zFvnYVrTTPuVfHUQzg0-qo7rF0K4_kqxdgOaw61H7u7fjqHqbkbryXjG_aVLakv2d9AIBV5N-mox6wKAbrlFY9-eUQnetYThaZEKZ8buu6GY_7DzE76QQYfYWgJMR5aAIOvmTE3pqZL1s9OuSK8EWaHCkJGrsvJVr4LGTUXF3cOd8o5SsdDjlYn-LjHrZCaLiS_Y6m75tRozFvRCjttpUOxaOybUuGZw8y0qjYrP_0JVbXQ1hhzoymauOxH_WnHUUgR3c9lHLE0P0g=w510-h368-s-no?authuser=0" alt="my alt text"/>
  <figcaption>From: <a href="https://ieeexplore.ieee.org/abstract/document/9459837">A Microcontroller based Charge Balanced Trapezoidal Stimulus Generator for FES System</a></figcaption>
</figure>

- This is actually a constant voltage controller. Practically all of the ones I found were a derivation of this circuit (this particular one being the most complex)
- Although calculating through this circuit isn't too bad, there is no negative feedback component that could remove variations due to temperature (transistors are pretty susceptible to this)

<html><br></html>

<figure style="text-align: center">
  <img src="https://lh3.googleusercontent.com/pw/AP1GczMTVI5kx_ClKoe53dq-l0G5dXF9TdjffeaC1p3E1ikQnV9as8J9pROjPKJmkRTYjWw8n0fqGPvNeQ8qG7SDLuR9XQGm4S03oX8xv7kuUNT51z9eEOEd1sqIDufatjVRNxXgBIoS2Z8ghdLU7H9UXrXEgJdZhffw1AgyHk3qK9P4DUIlweoPoKoRFuCsoEmXzNTzDqFzQfoWtnPcS_Z00o2SBqwIZMh4hKqMNfyWZhnh0r4UJYeMaDfpRx6yL30-tJ-Sf0bqYegcewT5XN95EuFjtv7keY2Uvi2uzPED09CYzuAs6UcmVgm39CtR078Lr4z7tbNdSLcxvBgsT1vpurknVZgsLgLMPN2Wu0PipaZPXmn7ePQNwB5C3GgITm0zbTWlG9n9T841OJrK-hgTxI2u9AyTJLv8Q7kHILNJyEqug5YOzMiJkrAjib_juaDq3RveOtoNIG6G2OUIj16xmzeoBRfrogEijg2ZG9tmhldnqI9JCXE9P8mkePZpGHGoJeH-3jjhZcjPLq8ZlUPOmvw6_PVwbqvxwdvdOwMVhZPHqBxAoGpor3cvlW-smvGmz3pIEy6FK5_zesvDo-OKCabiZE1WuRgJUKxxM5qrxE67Sqs1o72t-x9nmiu40mNhZYpDSUcEOw13TIT38Oh4uXpYLpIEVv9abZ3NtBRygSa_i5KgexQ1LSL7Qr_Ak_i8sneC-qIDiDAic6JIoM1ZxM8aM4uj-ue2zSNAMuDmJcY-Dfxo_Z25utqhGQprVy8-wUpS1GfrH4AHvfOt_-xu0u5A6TmC95KBK7dKTZUtUOgEZDKh3VNdJY1I6aEAavxYdYl7bIZafBA7XB2LGhERiiOQbJMOJVglgrQm69zSnW-d1ol8cskJDJW3-SpJRKKZhB1XcoATgwzqkpNWRRuprziY-gJPAZ0o9iSnIIVb98LIEFE-uuCt4obxo2WRrQ=w234-h257-s-no?authuser=0" alt="my alt text"/>
  <figcaption>From: <a href="https://ieeexplore.ieee.org/document/1020441">A Simple Constant-Current Neural Stimulator With Accurate Pulse-Amplitude Control</a></figcaption>
</figure>

- This is a cascode charge pump, with the current drive set by R5. This makes it difficult to change the current dynamically
- There were other charge pump designs, but I couldn't really see the reasoning behind using a charge pump. The use of mosfets stuck with me, however...

<html><br></html>

<figure style="text-align: center">
  <img src="https://lh3.googleusercontent.com/pw/AP1GczNfLw0LvGAwHlYUucwm8LNpWwKS78usPKfzhshksQUoJRAhTCIMRVAToyliDWeoa5me793sHVtjAM7AzKq7WPVX0JRm7kcl745NjFq0iyTgcdS0dCnwmGT7GkQdiQCZ9GI-n5yq88v22FsWZmuE5gcYcoIEZdEHLhIFWyx5QxH0-eDM-nZ83MG2Zm6RcgqZkKNuX6jyA0fNacSP3HuDLgmoR_KmUOxODPx_IJUSNksplgKdo6EmDAkyA9w3bJsGebQEl6eqt1bEHLjaTCMtwFc9kskFQOxokcdZ98EPA-mKkai6_7dWL1u6xMda-yTf9N3qM6L64afeGD9RsgTQNIVqNwnzteXtEuIoOr2170HUeK6T8hy0LAb_JUnlnYTvW8lbfzTvqIm7jn28ykshKSRPa-E1cvq0XGXU382Uhp0X0cc1LsX6MgvQTDGlkTAoL8i5XPE1-6t_2OYYP7SLukomYpELIH9wReb7GMZ-mhtr_0XCXRY5qUYR0rNuyBpHJqADJ4Cz_f9rK3jM430iO1ZKaz85sR8FwegM3knreqBlQKAHUftZ-BJbUIS-ZuW2cJ3Pgy69Dpuif9xCNOvGirV66MXlXhrscJM3mQGw9SWudCBUr2pGFNEdHz3kfAYn3cGxtrSEoyojRcPlcjDglR23eNgFdsqAaNJ_U9G3BOMU10ztLckPg2LOSXYZWXGIKcCBHS83pKTJCQWIHMSss9kw9oJCAi_iOhedWXP0zEtneXOItJUzY8jmXW1Nl_mTV_ax1HKHY91rR6BwkRYIaZroJZwpYTy0W9Ci-6hzqMjkau7uTKd_iU21uI3fevR5W43Aka6vraoRenLjhWFa-ftgWdLDH_PdS6JnDqAE-VCn6jwPg_ZD4PDun-0oWsrUZZ3nxe16HA_-DY08lz89teEuy2ewP1F1R6suVFN0sXt4NhJG7Pye-soOnZ_7CA=w348-h346-no?authuser=0" alt="my alt text"/>
  <figcaption>From: <a href="https://ieeexplore.ieee.org/document/775402">A High Voltage, Constant Current Stimulator for Electrocutaneous Stimulation Through Small Electrodes</a></figcaption>
</figure>

- A modified Howland current pump with a low-side op amp. The benefit is that it's easy to control current drive (you just set Vin). 
- Since this needs to (as calculated above) drive up to 120V, you need a specialized power op amp. In general, as the power requirement for op amps increase the other parameters, like slew rate, offset voltage, etc. get worse... which means that you need a _really_ specialized op amp. That's expensive. The [one](https://www.mouser.com/ProductDetail/Apex-Microtechnology/PA85A?qs=TiOZkKH1s2T44orxgXhYUg%3D%3D) this paper used is $250!! And you need two of them!

<html><br></html>

<figure style="text-align: center">
  <img src="https://lh3.googleusercontent.com/pw/AP1GczOFCwiKTAtyvDzLmxdjDGsBytXipVATCt528uZ7DP8xD7lUvYK_2GRZfIVIF2uZt5kExwANcOy2aLkzH2pRqn4DhUuhtLypJA-Mgv6uiNr48L9GXuGcw-BncBdVmauvbZCvy5t7xqd2gKuK2ME5uxPojKkPyB8AdznJi-1mHFtMadAWUTqB0GiMKm5iYw317_20pekAQGfGvUVqSfIcZzsJZ_MpFsAQnqa6yQ49gsB0HFTUDB9SDqcyjH3cW1N_Sk8DyaBse8IS3efYJPBUQaa5QOhCXk9nIh09x9l-gOr6vlfs3TQW0keIkVbDH9X2m_lxfIOlLBF1K2Okz5570OCZ5HrnUk8D_BLe8RxxuzGSCqc3ood5wn1zyeoj6lxI6NmEFDDXyJDO8gM2Wkv_8MAay6LetOXpmfl4_QBSmJ2eAniCQ1IC9C0f0rBACWh58UP3m6MM5nQ4RBvKDuZS8lMGFn7KNuJsJHH24j5De9rcK-aQeQmuZZhTuWP07EAV5DC0OXMqpfMxE6-16J14HYf7rrg0AeKc-7vV3kYZTtD3C8AFnehc8TVjAMVj94ERI9mOL_gh_Zskir8M4w9tD2raERMNze1bq23-7p8YblWHD5lXwG9X5xAnlRcgXoudtoEkaSEIWCfJkkEA335Oq7q1wMb1F-GxQatGzxdyj1dVw3AfXcePgBfIWcXKzcno34TdDe9BIFeIn5yy0W0OEesixm3V0Gy5HVOadTCZ_uAdLh_9I1KXGnpiUnPGGw5GFV08x10cnlamdVFuxbbeTje22FmOYRrWe1MhleZQr4hoItD4WB2rHaABqs1e12DqJq9COple0UTWsO-g9B3_TlVfOQvmt6uj9wHmVq8VXnIsorzL4z64xeBycD7HLO6dM7KGMjXI3A9kaN3synka8uTsexDld8gw_CPYHPmmNlQG8CY2PXFQJtvrFtza_g=w407-h454-s-no?authuser=0" alt="my alt text"/>
  <figcaption>From: <a href="https://pubmed.ncbi.nlm.nih.gov/1761295/">A 16-channel 8-parameter waveform electrotactile stimulation system</a></figcaption>
</figure>

- A really cool charge-pump-esque circuit that can drive both positive and negative voltages. It took me a while to understand what was going on here. It's really a beautiful circuit.
- This circuit was designed by five graduate students / professors working together. If I made a mistake recreating this, I wasn't sure if I could understand how to fix it. I also thought that things could be simpler. 

That said, reading all those papers led to some pretty concrete design requirements: 
<iframe src="https://drive.google.com/file/d/1e_qqD-9IH9uEzzEvokHVv_8L0woIGoLh/preview" width="640" height="480" allow="autoplay"></iframe>

## Designing

The real crux of the problem is figuring out how to create a varying voltage that adapts to the muscle resistance. Creating a constant current source is pretty simple: 

![Basic current source](https://lh3.googleusercontent.com/pw/AP1GczNJIzjjlZM-QBi5APNTBXivAnUcFYK4bsGLClPdvU90KhRn8z8Y8HVCg-9dMRcfte2qjSG3s4P3oETKiqAx9jC26c1dK3d8OhUiiMZNx3Mn2XY06N07WVzBXMRfIQTLIlMcEw_ar3xKN_s6adyjJBnfePqFNxdusrrSq8HozH-ISJbRa-MZ5fbRcm8DiyuSMBZ6Wcc2TqMhIpw0jHNyZOq7OWJrb2BrbJzKJBD51GDJCv522ciVU7vAV3gTf_lPmfPlGC3Rx2jPo5CUai48FgVTE8Lh_EsQCufgle8qMPl3o2_D8gghw0RQc38ZaT_0J__B90cL4ycLJYo1yKupGtX9Tg-0-3SMTcqU9ZQp9JqauHOfth5U9RXQ6vz6_yJySRhUl1fxbea2aIUjXEew7YuLbnLdK1wkDhye-BXK6Xm4SGIlKGRnHCjkaa3jwQP54mGePuHX3yoZJLOQmGo7dgMtZp7guhfYWi76pGEUx9MxrL6nnDR-w87g-FeD6QLwbywH4i32y0t8kfsEAKAB8Cx0ss7sFDHDksJr72slgeK1Z3zzBJmYcbFeQYHXO1Daulli-Dvb6oaU6jAVidxXqvY9lWnoa99UWAkO9MITgWPO5TN00mDNzS5TIFSn0DWpHQlH-DMrE_iDRy59_3wUl0Mjh6Hn4RLgv3h9q0-AFr8dUhy5eSZf3HPQwZ7IvExGpdVmG1eaoC4tNjPk9nI521NiJDNXUz8nlaBoQsrIRZBOYY1nx5idwyt0sOQa1Q6ia-0xwCNjXbNDDJJcKRJ48Xh-m5tiYF1ziznGUtuTMLfcb5kOb0w00wO8sdt9cy94FXDLf77Ly4ah7q2eGreeMlhNcVEKagCydruOX1HsUDp3W4zxGdo4jTt4G81jeXJ6s-H0EjJz3f5hJ45L55Ymhe4LUtRPVFpto8Ti5S2t_AcjDvvXI5HY48YV48_chg=w311-h397-no?authuser=0)


Assuming that the battery (I couldn't find a voltage source symbol) is a high impedance output and VDD can change to suit $ V_{DD} =  \frac{V_{Batt}}{R_{11}} R_{muscle} + V_{Batt} $, the current through $ R_{muscle} $ is just $ \frac{V_{Batt}}{R_{11}} $. How do you get $V_{DD}$ to change though? This is where mosfets come in. In saturation mode, mosfet $ V_{DS} $ can basically increase arbitrarily to satisfy KVL regardless of $ I_{D} $ (as long as $ I_{D} $ doesn't put it in the cutoff region). By sticking a mosfet in here, $ V_{DD} $ can stay constant, and with an op amp, the gate voltage can be easily controlled:


![Mosfet current source](https://lh3.googleusercontent.com/pw/AP1GczM8vGKxr0zVSZ02yvsWTLXUtgCI_SfsJzTVCncYVjIDZSvroNS7uZGNJkds7NPchT7eKtV7GcLYphkWd4pE9qbSxr4BRG036p9ZgDK7PeFKLM_lnPGsTx5lFdCoX4jGYKhgMT3mWR0rb4J48cIASu4P_hARwWJJjpeTjMqoMYY4ET_XMBGCaJakMsCGjJ5bVrKx8fWE57JBYglZ-5eJ8DgTapxluF_osTmSJpAr-F6-gWz9z7NtuU4GlEtvdoRWIEo7f7K9Cj4h_W6SBtKbQbfqRrPr6L7wD4Jgzr1GEx36yNCgOuVhh1CGyuZ9stiiXv7H_-KNrDF5pL6tcRVRXhxhK1_Gh0J03r0DfxVnNRk9S78EwLoAhYwR0rpj7G7RdImd585wzesucLuDL4Yxij4VOhQiEcYgcrRdJ6OxoTV36uJEuxnwJ9gZItnDWTgu8IJRNYYXJYjGk3_VCEXOpw0v6ez1SlO-l5ZqyoY6tFOlvgCWfmtFT-zdjTGQbqPodra5mcZVHfMEtOc9jzPZwEHwzrLciJFHae7LgL5OGDlWoHPj6nbATdoGobi-gmZENfTXfCfQujkdQN2z5bsbEI-Jz3NDn_ZrZ9fAdbS17BqpdZ_oOQ-w2RhlrJxebFVmjsP6LEpf6yLZjUIxsTdjaxhI3flVTVV3_hKctbRoZIvm1oLjApvP2_QQ1ATPla5hf59aI-lMbiTUw-leA1ZB9uujtQVkFOTMIBk7guHYIoaFgcPRau6xy6BHs7eLEU9QCARNQ82bceoE0Vp2QTHQXQ0CoxXbRH6LkgMliwaWeN2e98emkLuLcaWjdclm7pNY0bX0nle7XKyhaVF5tXAW5WHdnXU9x1WDwjqGE7FOLgYY7ns4yBCd5zbjqhEPfmTCGRemvFYdh1XLflarAnDHOAbmn_XaX-3GGC2dxA-6KSpTIr0C3KtlMxqwZPQ4_g=w1268-h1003-s-no?authuser=0)

The drain current can now easily be set with the battery voltage, and the op amp provides negative feedback on the current through the load path - if $ V_{GS} $ is too high for some reason, the increase in $ I_{D} $ will increase the voltage on the inverting input of the op amp, decreasing the output voltage, and thereby decreasing $ V_{GS} $ and $ I_{D} $. R25 helps with leakage current. 

The main benefit of this design is that it's pretty simple and super easy to change the current drive. $ I_{D} = I_{Stim} $ is still set by $ \frac{V_{Batt}}{R_{11}} $. 

I sat on this for a while, but still a bit worried about its success, looked around for some traditional constant current drivers. And flabbergasted, in a [TI application note](https://www.ti.com/lit/an/sboa327a/sboa327a.pdf?ts=1722618327664&ref_url=https%253A%252F%252Fwww.ti.com%252Ftool%252FCIRCUIT060014), I found this!

![Ti version](https://lh3.googleusercontent.com/pw/AP1GczPhUtB2w1k6w8m0_dcCX680Nk--qQRa7fz7v8Q8bfl_7FSkF8TEy-puq8B4cDblDNt3ynKYimGTdXD4BAHZoXeOykmowqCLZx1YzLR7YC-oHLLS1JBBXQJzPjTups4gXgnSCAZlAi6ipYSK8OiPyO8TnGZHTeED69DLbxm5ihdgaed5g8p8_ohKsFzuIwbOjcfLuxzgP3HOmDOmnhcHpIxNgFT82CgaLLMeQt8NgRgBgTS8N2Odta8aihAxeuHlgIICeRtGoqkahZD43Z62dqPkFZaZkpLCa7aoRJU_5XPOiP5j71FZwbzchw0r2F2-fHTbbeK8BuCFdv_qc4kNRaxPppWDposRSrhWj7OUQyXReR4qddAfY5mkwLoq8O1abNbPJTGeg-OwUYeMNRwGhp9ZRrQSPDbkpq6gA2Nu8s57ByMjCHRxY_YD6cGlKWGvj6jZ1E5Q_UMJ6mKOnuamjFfNMKqchZwiS_66USvYtb5scmsqVRsC0ju9v2tTEybugIT_y0laDuCDzEcJepI1fzKPkePBQ8tNpcNWUrNfdXpH4BwhjsutbTm2wuJP3HnsXJ9wcoqGAPQP1klbcENpoz6mdif2mPTDbN2vbZpYvXZ5vkHVTy7uiL5zz-HrU5uf120XRM2aT5uJok1RE0mpoJ_NYAN5Z_IEtAbB4mYRq1URwlfHvnhpjBw3uIpr79jzqVTDz84ndh19oL_GjMP72DWXsoY4cUjN6byh3yFnqHyTCkPC57kF1z01fpRism6rnX_TK97luwL96Uz8hdQTs2Ep-aBOGfEUHY0qk-M7ldoPq2t7IxQx5zIT7UDtTSgZ78xLWxh5Vst15cbg4CNDWwfnlWRlCvBZijXqetoFsu3BzCd4J9bkfkn6ML9WvJRl_brTmLtxsu__pwF5ALt0I7q1K_rx4tTyUj3aVjw4zHJVfqXUJgv_P-04C5tH9Q=w602-h608-s-no?authuser=0)

The only difference is C1, which they say is used to attenuate transient response. This makes sense, because mosfets have a gate-source capacitance that can cause ringing. C1 closes an RC circuit between $C_{GS}$, R1, C1, and R2, which means that you can control the transient response more easily with any of those components (preferably C1 and R2, since R1 is for limiting the transient gate current).

Also, a negative version of this can be made simply by making $ V_{DD} $ negative and changing the nmos to a pmos. 

### Simulation

I simulated the circuits in pSpice, copying the values for C1 and R6 from the Ti page. You can't really simulate these unless everything is identical to reality, so the plan was to tune these on the actual boards I ordered. 

Here's a DC sweep on the drive voltage, measuring the load current (negative version, although the positive one is identical but flipped):

![DC sweep](https://lh3.googleusercontent.com/pw/AP1GczMs-LlWx5mLsPkSgw3-etgWjsNXiVAoGlA4bW_og1pPG9704Lluir0a4hppfATOZ1ZX7XY0jbgaSdnAk6hI8inkvzx9S8A7C8sXJSVQdF1pR59XEU2O4MtNQRAecuANT168nkejfol1lm_Cjc9he83VyBkRmFH4aOy8E2mqDHSSUbWPTN021oUDq3NV661fCBnZ4ynN8Ckfa8CUUhqXn7pG-JJG3wukohPkHzEV2PsPzCPBFClEj3HvQjeoB3qEQmwYAWgFmLz1NS55jNV2ymH0Bk-K_2mSlpZ906Sczmf9wctwfXT7TP-sOGdTrG22q4jjTM20ikAaEPR-rbOMbKzEev7Ucm4CJJkmFHNyL3UJC9gawpC_wmbVxlgs4eU_gM975lB76bejmaqndIj0lyc6sIegwYEqp2T5ILXEe4gBFcuEMVPDslyZFc8x6vlwd3EW799FDSAtag3K0M7t_vOyXn1lJVCClkk43u5nQjj4f3Zdq3kBUS9a7e_Rkp1xnvoHrz9lTWEZZyZcec1pN4nptbizHCEcqKXuL_Pgb2L69CsMJZz71wBft7FaeEfTeUmLUFnMPHPL4Y4gU1ddb7A-xP-sGGZ2rbDlwJW_H-IrG0cWnYdTpnUMWeThHtNovV3kOpZl-yEJ_oyaK4mnaoZocT0IUSKGomkk-MFDfQByJrQ_scocTV4-G5lxrHdpky1Wsu1GYPcYgGPG2fxtfr4JxboVxhZLqj-b1InzC_PJG_MbBevzzi9PinRmCpWTL3ItsDX-BEltgn96cOjQYF-E7EewgK16u_ZQoo1KVCBvoCHX2VTXdtzWJSW0YYOm4s4g2ROJGPsg0MMwfqv3vg2XMm5gZ6H8hm1XJtvfdB-M_dahHsEL4p5s7aAcgPRsLrTq6JInZ7Zf2bskuQvRw7FWKWOtsDUa2n4Cw0B-GzGE7m7XahlYmPeaxBlZHQ=w1605-h1003-s-no?authuser=0)


And here's a transient step response of the positive version: 

![Transient step response](https://lh3.googleusercontent.com/pw/AP1GczOXyinEd_vQrtHC73cyClLLx_9fK54R041DyMW_3n5AAS8ldkKIaIcMrNniipkAQ0Ym2jyEChgIKCMWVyGB7eVmJiomVmfLB9wRFAeDzg_hohrgQCvU_qBe3LYmxWUW6YJH62ol_OtlsCa36AXv4A9C4COlJK5osWRHHfi6ZLseVL-sMFsHDzUiAbJpktpkU5fXZLuyog87-lO0KljNu3bq02URsGmg7quGdqGy-2ztIyQYjdbEe8ROmrLpCM4crTlVt_NcFyGKrF3p3IQQEkZNBF6XF97xN8yunw96mmsm98G15bH7ohjQs4o17c3-1cqX4_1avwvWjKGZSMWGZomynGVn4ukS1urzqQrtvlbSx9BuFu4Kp4KH7kzEeQ8ShYorxYyBGhqXXP450Tfu8urws-YnDBefq3AwLlOYu6dISmKMtyhnm_DjoX6omVUVq1xPuH1TJiZ3CFJkT9x8ba4tDa5xDukv8RaLpbedEUmeK_OmHsqC-dE-KHLBexvNsi49bObV46d0FMEDMevE7BGAyc3hEc5hnhWV331kjibnwDsR8jlSXu0MmxuymHKrQb7JgLzpTC03-NQjQyf4NQxaGSj1JM3tVnjYZRVh2DaccI1S3FunR1-1HDdC_woXOTCudToyRy_AsVoyckRaixNORJJ6r8hjfhN1XDEYy35XJAhQ_es4tbqOruDYiSg2wj5EdwJYbdEmbyjhbroZjYK80DbaU4yCkOKYAMcg2jaQeBQDIV2z5kwlO-Y2HWa5BuBUT2JdbM5VqyU6Yx-UlWitKUnDecifr99KslTB5xgqexza6ui3RyYX_LGnoy7DTFx8wDB4OjsKybcGvWNXcfkQ5l_ncGOb7aSqCAFThrI4nSFxZfCMjO2E0fnWcvt8oNOEjFvoIe4-nnrEAVlQeBrPSOWRm0WMMAoglSchYG91uicPscy1rf54fEbMgg=w1989-h770-s-no?authuser=0)

Obviously the transient simulation can't really be trusted (I don't have any parasitics modeled and I'm using different components anyway) but I wanted to get some confidence that system stability was somewhere in sight. The DC sweep was extremely satisfying, since that's exactly what I need. 

To make the waveform easy to control, I added an analog switch on the output of a small 12 bit DAC so it's just a matter of outputing PWM. This is what the driver looked like when (almost) complete: 

![Driver](https://lh3.googleusercontent.com/pw/AP1GczPCrOWZOJACNxO8tWdzE5S1O26kcgWc80z7XeP-kYdL1oslM5frpObUVRjwIoki19SgZ5SjxvZVM6GgZ5_y1NPL270ZVJwzIsDNby2lT_FPdblfxLJzXyFDJtMRT3Yi8iAvQwhO1zGdPEsnEN6b61pKuvTyFrz2M8rVENHUO4vRWuGpeBgdsmH-Ty3wuTZT6GhkmYYBFUeaiAFeFNpVhF35Kmb_oxT3JwVAHwRRRZQiibkmbnZ90TG-UssKn3f9SorAO3uzHAApO_D6Nlzai1UHbXncmfJmCJrYXx_tbs69k3QIMfbH0eqIxACI0O3HGb0Y4S2fGObZ8JtA7H2dHEs_IPf_miqeZI-_1qZ3df67i3s9EgS9weKxfg433jqb_QTT36lqplbWrxhABQfRVY7DyWPocqu4PO2i8N11Vdxw4KfzGqLk1m8boDQ3JyWYvugX7Vz95ufluk7vd6x5gMx8XdNFMc56l_M896NeoR-PwyFCoGSzWk1uIXAKsdzIVsh1H5xGPOHALaNu3OSNe5fAUkXMQipblhES4CFyatRvAIRRQ-Ck3j5hC4IjeyGbbJKMl8MW5xDEAE3TztDLRIE9LcUXUGpLZVzHGkfXWBVtkErOxZjBGAMtgtVMfGk-NU9Kw647abdmb0r8Fxneo6qHSdi9mB-h2DOw5PukkNs0PZlM-BRTnhLbD5ww6Vp7RROGt5BMbqu36c9bLovzztaOgMUVP0BAOsepjryDeyEoHcimTScPYe8MiW1v-bBnFPZEei76bGv7o8mxsOh73hVbp27H92DpKn1ImXJXMyLVIc4iz4R5kDzzGlaFQpkcwtBqckfhv5UWpo6lcp5EU2YqyQh2HfVKq67zBuOtc3TRCLf9CJ8zf4nc6jwn1CQ7Cd48DxDhnhpxpFnT2r1fEp_56n0JnsJ4IO_U5d6jkpjVYDVc8IQDn0Zo8owPNQ=w853-h364-no?authuser=0)

### Negative source

To achieve the negative current source, I originally thought about making a negative version of this (hence the negative simulation), but I quickly realized that this didn't really make any sense. All you really need is the same driver, but driving the load in the opposite direction. And if you're going to have two drivers working in opposite directions... why not save some components by having one driver and something to switch the polarity of the load? This would also possibly protect shoot-through for oppositely polarized drivers. Although it'd be nice to use solid-state switches for this, I they're too slow - they switch on the order of a few microseconds, which can become a pretty lare part of the stimulation waveform. Instead, I chose a high voltage [switch](https://ww1.microchip.com/downloads/en/DeviceDoc/HV2201.pdf) designed for ultrasound, with four switches oriented so that I could control whether the high or low side was connected to each side of the load. 

This was a mistake, but I'll explain that in the next post. 

### Revision 1

I decided to send everything out as a series of modules so it'd be easier to debug stuff that wasn't working. This resulted in a small driver board: 

![Driver](https://lh3.googleusercontent.com/pw/AP1GczPlNu2WPau_jE22dnysEOoCYxkxXhjk90FvsG6JDrpMm_VgjwEJbqap57czv0lcM3hBjYmmq8gU7Tq4OHl2PyYAD1EEtdhLD8Bgi3Y27rCJ22RSTTJPYWKcPJQ0hctHj0iIWvCIhjrdzuO5m_joVKtc2OOzzHr_y_kykKw0dlpeVhGehSPumDyPuQC_-k3S3gHeX-6YgDoKejFLZdFgIcFEn1DjlCceJ3E-gcf3f_j61p4QrN8YPow06QacD7SKkQvPcRcCr0VSl5DWB6VPIqON5jDFh6PeJn6Nx_lQpX0hIo55cNAtc7IMo1Pr2gSE-YjkCvzTUYPz3Kg1mdurWxffcqfPsBjLIL04cesUQrRitdbiamafPYb_ADU2e_kNPrwrsNLnckKbQpuIwgHjPYznVXEgqU6sWNQOlvg-M_EhBZe79pV2bbfYFwhqYDxqR8f2-VYLuZTzverPm0Wtu-UOOFYSsN9xsl7ww_oi3NqhRWU4cC2af15bdu6iqS14JQWvP36GcMSU8ZbpVFcnZAszW4UOCqj4HDwRXqUD96Rgyb2xdQ98W7V65OsAR2wnfOLpJ8V2n0Tg8YfDIw_GubrvEv6BE0lK-30sFEVPLhhV-cL_jHyCeh2Kx2UhkKm2IiQZNyH36DKVS9nR1B17E2U5b4S49xFkzHj7mLlGwR9qb0Po4rX4FQgYrVBIMqg2a8_VIrUcORgy0TWaZvKSkCeOFWeSUYA4spq1dftg18ITH2zht-vtEzeV4ZDilVQReqhhSLKkBJJGKAGXTAU4mA_jMGzMrICQy4RpgGso6N8GmtZAc-Qg90qzj9-v5XudFkoiuz-rrPYQvnSTS4H_UM003kOqtlIQMqus8xkjS66jZEqzJZYO7rgGmnC30EvZGwXuRSJs0Yq9wpxl1XJsbdoLYnScwk7KGlwOLtDkeVAB4F4kLhvCWuL1QWLMmw=w1008-h778-s-no?authuser=0)

A flyback converter module: 

![Driver](https://lh3.googleusercontent.com/pw/AP1GczPlNu2WPau_jE22dnysEOoCYxkxXhjk90FvsG6JDrpMm_VgjwEJbqap57czv0lcM3hBjYmmq8gU7Tq4OHl2PyYAD1EEtdhLD8Bgi3Y27rCJ22RSTTJPYWKcPJQ0hctHj0iIWvCIhjrdzuO5m_joVKtc2OOzzHr_y_kykKw0dlpeVhGehSPumDyPuQC_-k3S3gHeX-6YgDoKejFLZdFgIcFEn1DjlCceJ3E-gcf3f_j61p4QrN8YPow06QacD7SKkQvPcRcCr0VSl5DWB6VPIqON5jDFh6PeJn6Nx_lQpX0hIo55cNAtc7IMo1Pr2gSE-YjkCvzTUYPz3Kg1mdurWxffcqfPsBjLIL04cesUQrRitdbiamafPYb_ADU2e_kNPrwrsNLnckKbQpuIwgHjPYznVXEgqU6sWNQOlvg-M_EhBZe79pV2bbfYFwhqYDxqR8f2-VYLuZTzverPm0Wtu-UOOFYSsN9xsl7ww_oi3NqhRWU4cC2af15bdu6iqS14JQWvP36GcMSU8ZbpVFcnZAszW4UOCqj4HDwRXqUD96Rgyb2xdQ98W7V65OsAR2wnfOLpJ8V2n0Tg8YfDIw_GubrvEv6BE0lK-30sFEVPLhhV-cL_jHyCeh2Kx2UhkKm2IiQZNyH36DKVS9nR1B17E2U5b4S49xFkzHj7mLlGwR9qb0Po4rX4FQgYrVBIMqg2a8_VIrUcORgy0TWaZvKSkCeOFWeSUYA4spq1dftg18ITH2zht-vtEzeV4ZDilVQReqhhSLKkBJJGKAGXTAU4mA_jMGzMrICQy4RpgGso6N8GmtZAc-Qg90qzj9-v5XudFkoiuz-rrPYQvnSTS4H_UM003kOqtlIQMqus8xkjS66jZEqzJZYO7rgGmnC30EvZGwXuRSJs0Yq9wpxl1XJsbdoLYnScwk7KGlwOLtDkeVAB4F4kLhvCWuL1QWLMmw=w1008-h778-s-no?authuser=0)


It looks like this is getting a bit long... check out the next post!

---