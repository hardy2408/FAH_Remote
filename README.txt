###########################
############ README for the Folding@home remote client ##############
###########################
Author: Gerhard Vogt
e-mail: Gerhard@gerhard-vogt.de
Referenz: Folding@home https://foldingathome.org
################################
The application is written in python, version 3.7.7, together with the kivy environment.
With the kivy environment we are able to support a big range of target systems while maintaining the same 
source code.
Target systems are/will be:
- Android
- IOS
- Windows
- Raspberry Pi

The use case of the application is the following.
For the folding@home project there are clients for the different operating systems available.
But not all existing systems are supported, mainly as not every system has enough CPU power to perform 
the calculations. So with THIS FAH_Remote application you are getting a folding@home client application
that does not perform any calculation at all, but is only controlling other clients.
The following prerequisites must be fullfilled:
- Install the real folding@home client software on any of your machines (Linux, Windows,...)
- Configure the machines/clients that they are accessible in the network
- Remember the IP addresses of your client as you will need them later for configuring THIS application

As soon this is done you can start using THIS application and configure your clients.

Have fun!
