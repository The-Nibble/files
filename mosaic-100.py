import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_mosaic(image_dir, output_path, canvas_size=(1000, 500), grid_size=(20, 10), blur_strength=10):
    images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith(('jpg'))]
    
    print(f"Found {len(images)} images in directory {image_dir}")
    
    if not images:
        print("No images found in directory.")
        return
    
    # Load images and resize them
    cell_width = canvas_size[0] // grid_size[0]
    cell_height = canvas_size[1] // grid_size[1]
    resized_images = []
    
    for img_path in images:
        try:
            img = Image.open(img_path).resize((cell_width, cell_height))
            resized_images.append(img)
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
    
    print(f"Loaded {len(resized_images)} images for mosaic")
    
    # Create base canvas and fill it with all images
    canvas = Image.new('RGB', canvas_size, (255, 255, 255))
    
    # Place all images across the entire canvas
    index = 0
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            if index >= len(resized_images):
                # Wrap around if we need more images
                index = 0
            
            pos_x, pos_y = x * cell_width, y * cell_height
            canvas.paste(resized_images[index], (pos_x, pos_y))
            index += 1
    
    # Create '100' mask with much larger font
    mask = Image.new('L', canvas_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    
    # Try several font paths that might exist on macOS
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
    ]
    
    font = None
    for font_path in font_paths:
        try:
            # Use a much larger font size - about 80% of canvas height
            font = ImageFont.truetype(font_path, size=int(canvas_size[1] * 0.8))
            print(f"Using font: {font_path}")
            break
        except IOError:
            continue
    
    if not font:
        print("No suitable font found, using default")
        font = ImageFont.load_default()
    
    # Center the text properly
    text = "100"
    
    # Get text dimensions to center it
    try:
        # For newer Pillow versions
        left, top, right, bottom = mask_draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
    except AttributeError:
        # For older Pillow versions
        text_width, text_height = mask_draw.textsize(text, font=font)
    
    # Center text
    text_x = (canvas_size[0] - text_width) // 2
    text_y = (canvas_size[1] - text_height) // 2
    
    # Draw the "100" text
    mask_draw.text((text_x, text_y), text, fill=255, font=font)
    
    # Save mask for debugging
    mask.save("debug_mask.png")
    print("Saved mask image for debugging as debug_mask.png")
    
    # Create a blurred version of the canvas
    canvas_np = np.array(canvas)
    blurred_canvas_np = cv2.GaussianBlur(canvas_np, (blur_strength*2+1, blur_strength*2+1), 0)
    blurred_canvas = Image.fromarray(blurred_canvas_np)
    
    # Create final image by combining original and blurred versions using the mask
    mask_np = np.array(mask) / 255.0
    mask_np = np.stack([mask_np, mask_np, mask_np], axis=2)  # Expand to 3 channels
    
    combined_np = mask_np * np.array(canvas) + (1 - mask_np) * np.array(blurred_canvas)
    final_canvas = Image.fromarray(combined_np.astype(np.uint8))
    
    # Save the final mosaic
    final_canvas.save(output_path)
    print(f"Mosaic saved as {output_path}")

# Usage
create_mosaic('covers', '100.jpg')
