import os
import sys
import logging

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from utils.color_utils import ColorUtils
import io

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

class ColorPaletteBot:
    def __init__(self):
        self.color_utils = ColorUtils()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        welcome_text = """
🎨 Welcome to @colorpatebot!

I can help you generate beautiful color palettes. Here's what I can do:

1. Send me a color in HEX format (e.g., #FF5733)
2. Send me a photo/image to extract colors from it
3. Use /random to generate a random palette
4. Use /help to see all commands

Try it now! Send me a color or an image. 🖌️
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎲 Random Palette", callback_data='random'),
                InlineKeyboardButton("🌈 Color Wheel", callback_data='color_wheel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = """
🤖 Available Commands:

/start - Start the bot
/help - Show this help message
/random - Generate a random color palette

📸 Send me an image to extract its color palette!
🎨 Send me a HEX color code to generate a harmonious palette

Example: #FF5733

Made with ❤️ for your design projects!
        """
        await update.message.reply_text(help_text)
    
    async def random_palette(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a random color palette."""
        import random
        random_hex = f"#{random.randint(0, 0xFFFFFF):06x}"
        await self.process_color(update, context, random_hex)
    
    async def process_color(self, update: Update, context: ContextTypes.DEFAULT_TYPE, hex_color: str):
        """Process a hex color and generate palette"""
        try:
            # Validate hex color
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                await update.message.reply_text("❌ Invalid color format. Please use #RRGGBB format.")
                return
            
            hex_color = f"#{hex_color}"
            
            # Generate palette
            palette = self.color_utils.generate_palette(hex_color)
            
            # Create palette image
            img = self.color_utils.create_palette_image(palette)
            
            # Convert image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Get color name
            color_name = self.color_utils.get_color_name(hex_color)
            
            # Prepare caption
            caption = f"🎨 Color Palette based on {hex_color}\n"
            caption += f"📝 Color Name: {color_name}\n\n"
            caption += "🟣 Colors in palette:\n"
            for i, color in enumerate(palette, 1):
                caption += f"{i}. {color}\n"
            
            # Send the palette image
            await update.message.reply_photo(
                photo=img_bytes,
                caption=caption
            )
            
        except Exception as e:
            logger.error(f"Error processing color: {e}")
            await update.message.reply_text("❌ Sorry, I couldn't process that color. Please try again.")
    
    async def process_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process an image and extract color palette"""
        try:
            # Get the photo
            photo = update.message.photo[-1]
            file = await photo.get_file()
            
            # Extract colors from image
            palette = self.color_utils.extract_colors_from_image(file.file_path)
            
            # Create palette image
            img = self.color_utils.create_palette_image(palette)
            
            # Convert image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Prepare caption
            caption = "🎨 Color Palette extracted from your image!\n\n"
            caption += "🟣 Colors in palette:\n"
            for i, color in enumerate(palette, 1):
                caption += f"{i}. {color}\n"
            
            # Send the palette image
            await update.message.reply_photo(
                photo=img_bytes,
                caption=caption
            )
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            await update.message.reply_text("❌ Sorry, I couldn't process that image. Please try again with a clear image.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages containing hex colors"""
        text = update.message.text.strip()
        
        # Check if it's a hex color
        if text.startswith('#') and len(text) in [4, 7]:
            await self.process_color(update, context, text)
        else:
            await update.message.reply_text(
                "❌ Please send a valid HEX color code (e.g., #FF5733) or an image."
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'random':
            await self.random_palette(update, context)
        elif query.data == 'color_wheel':
            await query.edit_message_text(
                "🌈 Color Wheel feature coming soon! 🚀\n"
                "For now, try sending me a color or an image!"
            )
    
    def run(self):
        """Start the bot"""
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not found! Please set it in Railway Variables.")
            return
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("random", self.random_palette))
        
        application.add_handler(MessageHandler(filters.PHOTO, self.process_image))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start the bot
        logger.info("✅ Bot started successfully!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = ColorPaletteBot()
    bot.run()
