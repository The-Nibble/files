import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_mosaic(image_dir, output_path, canvas_size=(2000, 1000), grid_size=(40, 20), blur_strength=10):
    # Remove the output file and the debug_mask.png
    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists("debug_mask.png"):
        os.remove("debug_mask.png")

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

    # Create mask for text
    mask = Image.new('L', canvas_size, 0)
    mask_draw = ImageDraw.Draw(mask)

    # Try several font paths that might exist on macOS
    font_paths = [
        "/System/Library/Fonts/Menlo.ttc",  # Menlo - a popular monospace programming font
        "/System/Library/Fonts/SFMono-Regular.otf",  # SF Mono - Apple's monospace font
        "/System/Library/Fonts/Monaco.ttf",  # Monaco - classic macOS monospace font
        "/System/Library/Fonts/Courier.ttc",  # Courier - tech-looking monospace font
        "/System/Library/Fonts/Helvetica.ttc",  # Fallback to Helvetica if others not found
        "/System/Library/Fonts/SFNSDisplay.ttf",  # Final fallback
    ]

    # Find a suitable font
    font_large = None
    font_small = None
    for font_path in font_paths:
        try:
            # Use a large font size for "100" - about 60% of canvas height
            font_large = ImageFont.truetype(font_path, size=int(canvas_size[1] * 0.6))
            # Use a smaller font size for "NIBBLE" - about 20% of canvas height
            font_small = ImageFont.truetype(font_path, size=int(canvas_size[1] * 0.2))
            print(f"Using font: {font_path}")
            break
        except IOError:
            continue

    if not font_large or not font_small:
        print("No suitable font found, using default")
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Get dimensions for "100" text
    text_100 = "100"
    try:
        # For newer Pillow versions
        left_100, top_100, right_100, bottom_100 = mask_draw.textbbox((0, 0), text_100, font=font_large)
        text_100_width = right_100 - left_100
        text_100_height = bottom_100 - top_100
    except AttributeError:
        # Fallback for older Pillow versions
        # Note: textsize is deprecated but we'll keep it as a fallback
        try:
            text_100_width, text_100_height = mask_draw.textsize(text_100, font=font_large)
        except:
            # If both methods fail, estimate dimensions
            text_100_width = int(canvas_size[0] * 0.6)
            text_100_height = int(canvas_size[1] * 0.6)

    # Get dimensions for "NIBBLE" text
    text_nibble = "nibble"
    try:
        # For newer Pillow versions
        left_nibble, top_nibble, right_nibble, bottom_nibble = mask_draw.textbbox((0, 0), text_nibble, font=font_small)
        text_nibble_width = right_nibble - left_nibble
        text_nibble_height = bottom_nibble - top_nibble
    except AttributeError:
        # Fallback for older Pillow versions
        try:
            text_nibble_width, text_nibble_height = mask_draw.textsize(text_nibble, font=font_small)
        except:
            # If both methods fail, estimate dimensions
            text_nibble_width = int(canvas_size[0] * 0.3)
            text_nibble_height = int(canvas_size[1] * 0.2)

    # Add letter spacing
    letter_spacing_nibble = int(canvas_size[0] * 0.01)  # 1% of canvas width for NIBBLE
    letter_spacing_100 = int(canvas_size[0] * 0.02)     # 2% of canvas width for 100

    # Recalculate text widths with spacing
    text_nibble_width_with_spacing = text_nibble_width + letter_spacing_nibble * (len(text_nibble) - 1)
    text_100_width_with_spacing = text_100_width + letter_spacing_100 * (len(text_100) - 1)

    # Calculate total height of both texts with some spacing
    spacing = int(canvas_size[1] * 0.05)  # 5% of canvas height for spacing
    total_text_height = text_nibble_height + spacing + text_100_height

    # Center both texts vertically
    start_y = (canvas_size[1] - total_text_height) // 2

    # Center "NIBBLE" horizontally with spacing and position it at the top of the text area
    nibble_x = (canvas_size[0] - text_nibble_width_with_spacing) // 2
    nibble_y = start_y

    # Center "100" horizontally with spacing and position it below "NIBBLE"
    text_100_x = (canvas_size[0] - text_100_width_with_spacing) // 2
    text_100_y = nibble_y + text_nibble_height + spacing

    # Draw "NIBBLE" text with letter spacing
    current_x = nibble_x
    for char in text_nibble:
        # Get width of this character
        try:
            left, top, right, bottom = mask_draw.textbbox((0, 0), char, font=font_small)
            char_width = right - left
        except AttributeError:
            # Estimate character width
            char_width = text_nibble_width // len(text_nibble)

        # Draw the character
        mask_draw.text((current_x, nibble_y), char, fill=255, font=font_small)

        # Move to next character position with spacing
        current_x += char_width + letter_spacing_nibble

    # Draw "100" text with letter spacing
    current_x = text_100_x
    for char in text_100:
        # Get width of this character
        try:
            left, top, right, bottom = mask_draw.textbbox((0, 0), char, font=font_large)
            char_width = right - left
        except AttributeError:
            # Estimate character width
            char_width = text_100_width // len(text_100)

        # Draw the character
        mask_draw.text((current_x, text_100_y), char, fill=255, font=font_large)

        # Move to next character position with spacing
        current_x += char_width + letter_spacing_100

    # Create a border around the text to make it more distinct
    border_mask = mask.filter(ImageFilter.MaxFilter(size=9))  # Apply dilation to create border
    final_mask = Image.new('L', canvas_size, 0)

    # Create a thicker black border mask by applying MaxFilter multiple times with a valid size
    black_border_mask = mask.copy()
    # Apply MaxFilter multiple times to create a thicker border
    for _ in range(1):  # Apply 1 times for a thicker border
        black_border_mask = black_border_mask.filter(ImageFilter.MaxFilter(size=9))

    # Combine masks - original mask with high intensity, border with medium intensity
    final_mask_np = np.array(mask) * 0.9 + np.array(border_mask) * 0.7
    final_mask_np = np.clip(final_mask_np, 0, 255).astype(np.uint8)
    final_mask = Image.fromarray(final_mask_np)

    # Save mask for debugging
    final_mask.save("debug_mask.png")
    print("Saved mask image for debugging as debug_mask.png")

    # Create a blurred version of the canvas using PIL instead of cv2
    blurred_canvas = canvas.copy()
    for _ in range(blur_strength):
        blurred_canvas = blurred_canvas.filter(ImageFilter.BLUR)

    # Convert the blurred background to grayscale
    # blurred_canvas = blurred_canvas.convert('L').convert('RGB')

    # Create final image by combining original and blurred versions using the mask
    final_mask_np = np.array(final_mask) / 255.0
    black_border_mask_np = np.array(black_border_mask) / 255.0
    text_mask_np = np.array(mask) / 255.0

    # Create border effect by subtracting the text area from the dilated border
    border_only_mask = black_border_mask_np - text_mask_np
    border_only_mask = np.clip(border_only_mask, 0, 1)

    # Expand masks to 3 channels for RGB blending
    final_mask_np = np.stack([final_mask_np, final_mask_np, final_mask_np], axis=2)
    border_only_mask = np.stack([border_only_mask, border_only_mask, border_only_mask], axis=2)

    # Combine: color for the text area, B&W for the background with reduced opacity
    # Reduce background opacity by adjusting the blending ratio
    text_opacity = 1.0  # Keep text at full opacity
    background_opacity = 0.7  # Reduce background opacity to 70%

    # Adjust the blending formula to incorporate background opacity and black border
    combined_np = (
        final_mask_np * np.array(canvas) * text_opacity +  # Original text
        border_only_mask * np.array([0, 0, 0]) +  # Black border
        (1 - final_mask_np - border_only_mask) * np.array(blurred_canvas) * background_opacity +
        (1 - final_mask_np - border_only_mask) * (1 - background_opacity) * 255  # Add white for transparency
    )

    combined_np = np.clip(combined_np, 0, 255).astype(np.uint8)
    final_canvas = Image.fromarray(combined_np)

    # Add a subtle edge enhancement to make the transition more distinct
    final_canvas = final_canvas.filter(ImageFilter.EDGE_ENHANCE)

    # Delete the debug_mask.png
    os.remove("debug_mask.png")

    # Save the final mosaic
    final_canvas.save(output_path, quality=95)  # Higher JPEG quality
    print(f"High-quality mosaic saved as {output_path}")

# Usage
create_mosaic('covers', os.path.join('covers', '100.jpg'))
