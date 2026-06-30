import os
import sys
import logging
import asyncio
import traceback

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

# Get token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Check token
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found! Please set it in Railway Variables.")
    sys.exit(1)

if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    logger.error("❌ BOT_TOKEN is still the placeholder! Please set your actual token.")
    sys.exit(1)

class ColorPaletteBot:
    def __init__(self):
        try:
            self.color_utils = ColorUtils()
            logger.info("✅ ColorUtils initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ColorUtils: {e}")
            sys.exit(1)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        try:
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
            logger.info(f"✅ Start command sent to user {update.effective_user.id}")
        except Exception as e:
            logger.error(f"❌ Error in start_command: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
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
        try:
            import random
            random_hex = f"#{random.randint(0, 0xFFFFFF):06x}"
            await self.process_color(update, context, random_hex)
        except Exception as e:
            logger.error(f"❌ Error in random_palette: {e}")
            await update.message.reply_text("Sorry, couldn't generate random palette. Please try again.")
    
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
            logger.info(f"✅ Sent palette for {hex_color} to user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing color: {e}")
            logger.error(traceback.format_exc())
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
            logger.info(f"✅ Extracted palette from image for user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing image: {e}")
            logger.error(traceback.format_exc())
            await update.message.reply_text("❌ Sorry, I couldn't process that image. Please try again with a clear image.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages containing hex colors"""
        try:
            text = update.message.text.strip()
            
            # Check if it's a hex color
            if text.startswith('#') and len(text) in [4, 7]:
                await self.process_color(update, context, text)
            else:
                await update.message.reply_text(
                    "❌ Please send a valid HEX color code (e.g., #FF5733) or an image."
                )
        except Exception as e:
            logger.error(f"❌ Error in handle_message: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data == 'random':
                await self.random_palette(update, context)
            elif query.data == 'color_wheel':
                await query.edit_message_text(
                    "🌈 Color Wheel feature coming soon! 🚀\n"
                    "For now, try sending me a color or an image!"
                )
        except Exception as e:
            logger.error(f"❌ Error in button_callback: {e}")
            await query.edit_message_text("Sorry, something went wrong. Please try again.")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"❌ Update {update} caused error {context.error}")
        logger.error(traceback.format_exc())
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "Sorry, an error occurred. Please try again later."
                )
        except:
            pass
    
    def run(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting ColorPaleteBot...")
            
            # Create application
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Add error handler
            application.add_error_handler(self.error_handler)
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("random", self.random_palette))
            
            application.add_handler(MessageHandler(filters.PHOTO, self.process_image))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Start the bot
            logger.info("✅ Bot is ready and polling for updates...")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)

if __name__ == '__main__':
    logger.info("🐍 Bot process started")
    bot = ColorPaletteBot()
    bot.run()
