import time
import busio
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

class OLEDDisplay:
    def __init__(self):
        self.i2c = busio.I2C(SCL, SDA)
        self.disp = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c)

        # Clear display.
        self.disp.fill(0)
        self.disp.show()

        # Create blank image for drawing
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new("1", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load font 
        self.font_size = 13 
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)

    def clear_display(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.disp.image(self.image)
        self.disp.show()

    def update_display(self, line1, line2, line3):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        # Calculate text sizes
        line1_bbox = self.draw.textbbox((0, 0), line1, font=self.font)
        line2_bbox = self.draw.textbbox((0, 0), line2, font=self.font)
        line3_bbox = self.draw.textbbox((0, 0), line3, font=self.font)

        line1_height = line1_bbox[3] - line1_bbox[1]
        line2_height = line2_bbox[3] - line2_bbox[1]
        line3_height = line3_bbox[3] - line3_bbox[1]

        # y-coordinate to move lines 4 pixels up
        offset = -4

        # Draw the first line
        self.draw.text(
            (0, (self.height // 6 - line1_height // 2) + offset),
            line1,
            font=self.font,
            fill=255,
        )

        # Draw the second line
        self.draw.text(
            (0, (self.height // 2 - line2_height // 2) + offset),
            line2,
            font=self.font,
            fill=255,
        )

        # Draw the third line
        self.draw.text(
            (0, (5 * self.height // 6 - line3_height // 2) + offset),
            line3,
            font=self.font,
            fill=255,
        )

        # Display image
        self.disp.image(self.image)
        self.disp.show()

if __name__ == "__main__":
    display = OLEDDisplay()
    display.update_display("OLED Display", "Setup", "Successfully")
