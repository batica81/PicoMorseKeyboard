# This code is taken from many places and many authors and compiled by YU4HAK :)

# Raspberry Pi Pico is needed to use this app! Maybe I will do an Arduino version in the future.
# Basic purpose of the app is to take input from serial port and turn it into Morse code.
# Then it plays it via sound, light or by acting as a straight key and triggering an external device (radio).
# Interfacing with the external device can be done with an optocupler, transistor, relay or similar simple circuit.
# There is one memory slot that can be played with a button push, and changed through console.
# WPM and sidetone frequency can be changed as well.
# Code has many bugs, please fix them :)
# 73


import time, sys, utime  # import necessary libraries,
from machine import Pin, PWM, Timer

led = Pin(25, Pin.OUT)  # the LED on the Pico is pin 25
digitalOut = Pin(9, Pin.OUT)  # output to trigger external device
button = Pin(10, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(15))

stdin_string = sys.stdin
lastInterrupt = 0
timer = Timer(-1)

memory1 = "CQ DE YU4HAK"
BlinkRate = 0.062
BuzzFrequency = 600

    
# functions for morse code signal durations
def dah():
    led.value(1)
    digitalOut.value(1)
    buzzer.duty_u16(1000)
    time.sleep(3 * BlinkRate)
    led.value(0)
    digitalOut.value(0)
    buzzer.duty_u16(0)
    time.sleep(BlinkRate)


def dit():
    led.value(1)
    digitalOut.value(1)
    buzzer.duty_u16(1000)
    time.sleep(BlinkRate)
    led.value(0)
    digitalOut.value(0)
    buzzer.duty_u16(0)
    time.sleep(BlinkRate)


def pause(elementcount):
    time.sleep(elementcount * BlinkRate)


# morse code conversion
code = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.",
        "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.",
        "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-",
        "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
        "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
        "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
        ".": ".-.-.-",
        ",": "--..--",
        "?": "..--..",
        "/": "--..-.",
        "@": ".--.-.",
        " ": "|",
        "-": "-....-",
        "(": "-.--.",
        ")": "-.--.-",
        "'": ".----.",
        "!": "-.-.--",
        "&": ".-...",
        ":": "---...",
        ";": "-.-.-.",
        "=": "-...-",
        "_": "..--.-",
        "\"": ".-..-.",
        "$": "...-..-",
        "{": ".--.-.",
        "}": ".--.-.",
        "+": ".-.-."
        }


# Function that returns morse code sentence from uppercase English sentence
def convertToMorseCode(sentence):
    tempSentence = sentence.upper()  # make it all caps so that the dictionary understands the character
    workSentence = ""  # empty sentence to add to
    for j in tempSentence:  # for each character in the sentence, reference code dictionary and change to morse code character
        if j in code:
            workSentence += code[j] + " "
    return workSentence


# main function that blinks LED based on morse code sentence
def sendMessage(sendSentence):
    secretSentence = convertToMorseCode(sendSentence)
    print("Sending: ")
    print(secretSentence)
    for i in secretSentence:
        if i == ".":
            dit()
        elif i == "-":
            dah()
        elif i == "|":
            pause(1)  # With two pauses of 3 elements, adds up to 7
        else:
            pause(3)


# A rough workout: seconds per dit:  60 / (50 * WPM)
def setWPM(wpm):
    global BlinkRate
    BlinkRate = 60 / (50 * wpm)
    print(BlinkRate)


def setBuzzFrequency(freq):
    buzzer.freq(freq)


def debounce(pin):
    # Start or replace a timer, and trigger on_pressed.
    timer.init(mode=Timer.ONE_SHOT, period=1000, callback=on_pressed)
    
    
def on_pressed(timer):
    sendMessage(memory1)


# Initializing app
button.irq(trigger = Pin.IRQ_FALLING, handler = debounce)
setBuzzFrequency(600)
setWPM(25)


# Keeps reading from stdin and quits only if the word 'exit' is there
# This loop, by default does not terminate, since stdin is open
print("Enter a parameter to change it, or text to send:")
for line in stdin_string:
    # Remove trailing newline characters using strip()
    cleanLine = line.strip()
    if '_SPEED=' == cleanLine[0:7]:
        newSpeed = cleanLine.split('=')[1]
        setWPM(int(newSpeed))
        print('Setting speed to ' + newSpeed + ' WPM')
        
    elif '_BUZZ=' == cleanLine[0:6]:
        newBuzz = cleanLine.split('=')[1]
        setBuzzFrequency(int(newBuzz))
        print('Setting buzzer frequency to ' + newBuzz + ' Hz')   
        
    elif '_MEM1=' == cleanLine[0:6]:
        newMem = cleanLine.split('=')[1]
        memory1 = newMem
        print('Setting memory 1 to "' + newMem + '"')            
        
    else:
        sendMessage(cleanLine)

