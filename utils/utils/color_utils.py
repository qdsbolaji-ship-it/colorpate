import colorsys
import webcolors
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from colorthief import ColorThief
import tempfile

class ColorUtils:
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb):
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def get_color_name(hex_color):
        """Get closest color name"""
        try:
            rgb = ColorUtils.hex_to_rgb(hex_color)
            return webcolors.rgb_to_name(rgb)
        except:
            return "Unknown"
    
    @staticmethod
    def generate_palette(hex_color, num_colors=5):
        """Generate a color palette based on a base color"""
        rgb = ColorUtils.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        
        palette = []
        
        # Generate harmonious colors
        for i in range(num_colors):
            hue_shift = i * 0.15  # 15% hue shift
            new_h = (h + hue_shift) % 1.0
            
            # Vary saturation and value for interest
            new_s = min(1.0, s + (i * 0.05) - 0.1)
            new_v = min(1.0, v + (i * 0.05) - 0.1)
            
            rgb_color = colorsys.hsv_to_rgb(new_h, max(0, new_s), max(0, new_v))
            hex_color_out = ColorUtils.rgb_to_hex(tuple(int(c * 255) for c in rgb_color))
            palette.append(hex_color_out)
        
        return palette
    
    @staticmethod
    def create_palette_image(colors, width=800, height=200):
        """Create an image of the color palette"""
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        color_width = width // len(colors)
        
        for i, color in enumerate(colors):
            x = i * color_width
            draw.rectangle([x, 0, x + color_width, height], fill=color)
            
            # Add hex code on the image
            try:
                font = ImageFont.load_default()
                text = color
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_x = x + (color_width - text_width) // 2
                text_y = height - text_height - 10
                
                # Add white background to text for readability
                draw.rectangle(
                    [text_x - 5, text_y - 5, text_x + text_width + 5, text_y + text_height + 5],
                    fill='white'
                )
                draw.text((text_x, text_y), text, fill='black', font=font)
            except:
                pass
        
        return img
    
    @staticmethod
    def extract_colors_from_image(image_url, num_colors=5):
        """Extract dominant colors from an image URL"""
        response = requests.get(image_url)
        img_data = response.content
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(img_data)
            temp_file.flush()
            color_thief = ColorThief(temp_file.name)
            palette = color_thief.get_palette(color_count=num_colors)
            
            # Convert RGB to HEX
            hex_palette = [ColorUtils.rgb_to_hex(rgb) for rgb in palette]
            return hex_palette
