# K-Door-Pi

Client for K-Space door system. Run on Raspberry Pi and controlls the doors

# Requirements

This project needs at least Linux kernel 4.8 and uses crossplatform [libgpiod]
to talk to the hardware. Under Debian/Ubuntu you have to install [python3-libgpiod].

    sudo apt install python3-libgpiod


[libgpiod]: https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/about/
[python3-libgpiod]: https://packages.debian.org/sid/python3-libgpiod

