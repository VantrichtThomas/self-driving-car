# Project IV: Self driving car
`Arne Lavaert & Thomas Vantricht`
`3MCT Smart tech & AI`

This Project lets a car drive between two lines of tape and stop at a red traffic light. It will start driving again when the light turns green.

Manual to install this project on your own raspberry pi.

## Requirements
### Hardware
- Raspberry Pi 3B+
- Webcam
- Powerbank for Raspberry Pi
- Traffic light
    - 3D printed case
    - Green, yellow and red led
    - 220 Ω resistors `3x`
    - Wemos d1 mini microcontroller
    - Jumper wires `male to male`
- Car
    - RC car
    - Servo motor
    - L298N H-bridge
    - Jumper wires `all types`
    - 3D printed parts
    - Battery for motors `[7.2V- 9.6V]`
- Blue painters tape

### Software
- Laptop/desktop
    - Putty/Terminal for SSH
- Raspberry Pi
    - Git
    - Python3


## Raspberry Pi software preparations
This manual requires a (clean) installed Raspberry Pi with a wireless internet connection and SSH enabled.


1. Connect via SSH to your Pi (both your pc and the Pi should be connected to the same network)
    ```bash
    $ ssh <user>@<hostname>.local
    > Enter your password
    ```
2. Update and upgrade the package lists
    ```bash
    $ sudo apt update && sudo apt upgrade
    ```
3. Verify python3 installation
    ```bash
    $ python3 --version
    > Python 3.x.x
    ```
4. Install pip3
    ```bash
    $ sudo apt install python3-pip
    ```
5. Install git
    ```bash
    $ sudo apt install git
    ```
6. Clone our github repository
    ```bash
    $ git clone <INSERT_FINAL_LINK_GIT.git>
    ```
7. Go the the repo director
    ```bash
    $ cd ./self-driving-car
    ```
8. Install all required pip packages
    ```bash
    $ pip3 install -r requirements.txt
    ```
9. Start the script
    ```bash
    $ python3 app.py
    ```


## Car modifications
1. Remove the front wheels from the car
2. Add servo motor with 3D printed bracket
3. Add a wheel to the servo motor.
4. Wire up

### Wiring diagram
- Wire the Raspberry Pi, servo motor and RGB Led like the schema below.
- Plug the webcam into an USB port.

![Breadboard](https://i.imgur.com/nOB73XC.png)
![Schematic](https://i.imgur.com/B6AXt9e.png)

## Test car
1. Draw two lines with blue painters tape on the floor `±40cm from each other`
2. Place the car in the middle of the two lines
3. Place the traffic light right next to a straight piece of the road for optimal results.

<img src="https://i.imgur.com/bYsWuZP.jpg" width="400" height="550" alt="parkour"></img>

4. Turn on the car, with the pi connected to the powerbank.
5. Connect via SSH to your Pi (both your pc and the Pi should be connected to the same network)
   ```bash
   $ ssh <user>@<hostname>.local
   > Enter your password
   ```
5. Start the detection script by following command
    ```bash
    $ cd self-driving-car && python3 traffic_light_detector.py
    ```
5. Wait for the program to start. (It can take up to 2 minutes)
6. Stop the program by hitting `Ctrl + c`
7. Start the lane following script by following command
    ```bash
    $ python3 lane_follower_and_detection_threaded.py
    ```
