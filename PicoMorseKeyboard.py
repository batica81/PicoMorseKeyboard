# This code is taken from many places and many authors and compiled by YU4HAK :)

# Raspberry Pi Pico is needed to use this app! Maybe I will do an Arduino version in the future.
# Basic purpose of the app is to take input from serial port and turn it into Morse code.
# Then it plays it via sound, light or by acting as a paddle and triggering an external device (radio).
# Interfacing with the external device can be done with an optocupler, transistor, relay or similar simple circuit.
# There is one memory slot that can be played with a button push, and changed through console.
# WPM and sidetone frequency can be changed as well.
# Code has many bugs, please fix them :)
# 73


import time, sys, utime  # import necessary libraries,
from machine import Pin, PWM, Timer
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


#real_freq = 17200

real_freq = 7020000


ledState = False

keyerButton = Pin(19, Pin.IN, Pin.PULL_UP)  # Morse key button
led = Pin(25, Pin.OUT)                      # The LED on the Pico is pin 25
digitalOut = Pin(5, Pin.OUT)                # Output to trigger external device
memoryButton = Pin(11, Pin.IN, Pin.PULL_UP) # Play memory
buzzer = PWM(Pin(8))                        # PWM buzzer
rfOut = 2                                   # RF out pin
rfOut2 = 3

stdin_string = sys.stdin
timer = Timer(-1)

memory1 = "VVV"


# 180 degrees inverted. WORKS !!!
# @asm_pio(set_init=(PIO.OUT_LOW,PIO.OUT_LOW))
# def square():
#     wrap_target()
#     set(pins, 0b10)
#     set(pins, 0b01)
#     wrap()
#     

# 90 degrees. WORKS !!! (double the sm freq!)
@asm_pio(set_init=(PIO.OUT_LOW,PIO.OUT_LOW))
def square():
    wrap_target()
    set(pins, 0b10)
    set(pins, 0b11)
    set(pins, 0b01)
    set(pins, 0b00)
    wrap()
    

def setFreq(real_freq):
    global sm
    sm = rp2.StateMachine(0, square, freq=real_freq*2, set_base=Pin(rfOut, rfOut2))

def vfoOn():
    ledState = True
    sm.active(ledState)
    led(ledState)
    digitalOut.value(1)
    buzzer.duty_u16(1000)
   # print("Led is:" + str(ledState))

def vfoOff():
    ledState = False
    sm.active(ledState)
    led(ledState)
    digitalOut.value(0)
    buzzer.duty_u16(0)
    # print("Led is:" + str(ledState))
    # print("Freq is:" + str(real_freq))

   
# functions for morse code signal durations
def dah():
    vfoOn()
    time.sleep(3 * BlinkRate)
    vfoOff()
    time.sleep(BlinkRate)


def dit():
    vfoOn()
    time.sleep(BlinkRate)
    vfoOff()
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
        "/": "-..-.",
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
            pause(2)  # With two pauses of 3 elements, adds up to 7
        else:
            pause(2)


# A rough workout: seconds per dit:  60 / (50 * WPM)
def setWPM(wpm):
    global BlinkRate
    BlinkRate = 60 / (50 * wpm)
    print(BlinkRate)

def setBuzzFrequency(freq):
    buzzer.freq(freq)

def onMemmoryButtonPressed(timer):
    sendMessage(memory1)
    
def debounceMemoryHandler(pin):
    timer.init(mode=Timer.ONE_SHOT, period=200, callback=onMemmoryButtonPressed)

# add debounce timer maybe
def keyerHandler(keyerButton):
    if (keyerButton.value() == 0):
        vfoOn()
    else:
        vfoOff()

# Initializing app

memoryButton.irq(handler = debounceMemoryHandler, trigger = Pin.IRQ_FALLING)
keyerButton.irq(handler = keyerHandler, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING)
setBuzzFrequency(800)
setWPM(20)
setFreq(real_freq)

#sendMessage("v")
vfoOn()

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
        
    elif '_FREQ=' == cleanLine[0:6]:
        newFreq = cleanLine.split('=')[1]
        setFreq(int(newFreq))
        print('Setting frequency (close) to "' + newFreq + '"')

    if '+' == cleanLine[0:1]:        
        real_freq = real_freq + 1000
        setFreq(int(real_freq))
        vfoOn()
        print('Setting freq to ' + str(real_freq))
        
    elif '-' == cleanLine[0:1]:
        real_freq = real_freq - 1000
        setFreq(int(real_freq))
        vfoOn()
        print('Setting freq to ' + str(real_freq))
        
    elif '0' == cleanLine[0:1]:
        vfoOff()
               
    else:
        sendMessage(cleanLine)
