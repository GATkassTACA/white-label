# Simple Python script to create a basic favicon for the pharmacy app
from PIL import Image, ImageDraw
import os

# Create a 32x32 image with a pharmacy cross
img = Image.new('RGBA', (32, 32), (33, 150, 243, 255))  # Blue background
draw = ImageDraw.Draw(img)

# Draw white cross (pharmacy symbol)
draw.rectangle([14, 6, 17, 25], fill=(255, 255, 255, 255))  # Vertical bar
draw.rectangle([6, 14, 25, 17], fill=(255, 255, 255, 255))  # Horizontal bar

# Add small colored dots for pills
draw.ellipse([8, 8, 12, 12], fill=(76, 175, 80, 255))   # Green pill
draw.ellipse([20, 20, 24, 24], fill=(255, 152, 0, 255))  # Orange pill

# Save as ICO
img.save('static/favicon.ico', format='ICO', sizes=[(32, 32)])
print("✅ Favicon created successfully!")
