import cv2
import numpy as np
import webbrowser
import pyttsx3

from cvzone.HandTrackingModule import HandDetector

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Keyboard layout
keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],       # Row 1: Numbers
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],       # Row 2: Letters
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],            # Row 3: Letters
    ["Z", "X", "C", "V", "B", "N", "M"],                      # Row 4: Letters
    [".", ",", "?", "!", "Space", "<--", "Del"],              # Row 5: Punctuation + Space, Backspace, Del
    ["Search", "Speak", "Save", "Clear", "Exit"]              # Row 6: Functional Keys
]
# Text typed by the user
finalText = ""

# Text-to-speech engine
engine = pyttsx3.init()

# Button class
class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, img):
        x, y = self.pos
        w, h = self.size
        # Transparent button background
        overlay = img.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
        # Button text
        cv2.putText(img, self.text, (x + 15, y + 55),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    def isHovered(self, cursor):
        x, y = self.pos
        w, h = self.size
        return x < cursor[0] < x + w and y < cursor[1] < y + h


# Create button list
buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        if i == 5:  # Functional keys (last row to be vertical column)
            x_offset = 1100  # Position slightly inward from the screen's right edge
            y_offset = 140  # Match spacing with the number row
            buttonSize = (140, 85)  # Larger size for functional keys
            buttonPosition = (x_offset, y_offset + j * 90)  # Ensure consistent vertical spacing
        elif i == 4:  # Row 5: Punctuation + Space, Backspace, Del
            x_offset = 50
            spacing = 120
            buttonSize = (110 if key == "Space" else 85, 85)  # Space is wider
            buttonPosition = (x_offset + j * spacing, 140 + i * 100)  # Prevent overlap with input box
        else:  # Rows 1-4: Numbers and Letters
            x_offset = 50
            spacing = 90
            buttonSize = (85, 85)  # Standard size for numbers and letters
            buttonPosition = (x_offset + j * spacing, 140 + i * 100)  # Prevent overlap with input box
        buttonList.append(Button(buttonPosition, key, size=buttonSize))
        
# Variables for press delay
lastKeyPressTime = 0
hoverStartTime = 0
hoveringKey = None
pressCooldown = 0.3  # Cooldown in seconds
hoverTimeRequired = 0.7  # Time required to press a key while hovering

# Updated Section for Functional Improvements

while True:
    # Get image frame
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Detect hands
    hands, img = detector.findHands(img, flipType=False)

    # Draw buttons
    for button in buttonList:
        button.draw(img)

    # Check for hand input
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        cursor = lmList[8][:2]  # Index finger tip

        for button in buttonList:
            if button.isHovered(cursor):
                # Highlight hovered key
                cv2.rectangle(img, button.pos,
                              (button.pos[0] + button.size[0], button.pos[1] + button.size[1]),
                              (0, 255, 0), 3)

                # Check hover duration
                if hoveringKey != button.text:
                    hoveringKey = button.text
                    hoverStartTime = cv2.getTickCount()

                # Calculate hover duration
                hoverDuration = (cv2.getTickCount() - hoverStartTime) / cv2.getTickFrequency()

                # Key press logic
                if hoverDuration > hoverTimeRequired:
                    hoveringKey = None
                    if button.text == "Del":
                        finalText = ""  # Clear all text
                    elif button.text == "<--":
                        finalText = finalText[:-1]  # Remove last character
                    elif button.text == "Search":
                        webbrowser.open(f"https://www.google.com/search?q={finalText}")  # Open typed URL
                    elif button.text == "Speak":
                        engine.say(finalText)  # Speak typed text
                        engine.runAndWait()
                    elif button.text == "Save":
                        with open("typed_text.txt", "w") as f:
                            f.write(finalText)  # Save typed text to file
                        # Confirmation message
                        cv2.putText(img, "Text Saved!", (50, 140), 
                                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
                    elif button.text == "Clear":
                        finalText = ""  # Reset text
                    elif button.text == "Exit":
                        cap.release()
                        cv2.destroyAllWindows()
                        exit()
                    elif button.text == "Space":
                        finalText += " "  # Add a space
                    else:
                        finalText += button.text

    # Display the typed text with a blinking cursor
    overlay = img.copy()
    cv2.rectangle(overlay, (50, 30), (1230, 100), (50, 50, 50), -1)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    
    # Cursor effect
    if int(cv2.getTickCount() / cv2.getTickFrequency()) % 2 == 0:  # Blinking effect
        displayText = finalText + "|"
    else:
        displayText = finalText
    
    cv2.putText(img, displayText, (60, 80), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    # Show the frame
    cv2.imshow("AI Virtual Keyboard", img)

    # Exit condition
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
