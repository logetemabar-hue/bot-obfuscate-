import discord
from discord.ext import commands
from discord import app_commands
import io
import os
import logging
from obfuscator import LuaObfuscator
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SanzzLuaBot')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

HEADER = """--[[
================================================================
          ███████╗ █████╗ ███╗   ██╗███████╗███████╗
          ██╔════╝██╔══██╗████╗  ██║╚══███╔╝╚══███╔╝
          ███████╗███████║██╔██╗ ██║  ███╔╝   ███╔╝ 
          ╚════██║██╔══██║██║╚██╗██║ ███╔╝   ███╔╝  
          ███████║██║  ██║██║ ╚████║███████╗███████╗
          ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
                   SANZZLUA ObfuscatorAnti-AI
                      (LUA / PWN / HTML)
================================================================
  Website     : https://dazzling-shortbread-a9ec1f.netlify.app
  Obfuscation : Runtime polymorphic
  Anti-tamper : C verification
  Entropy     : High
  Status      : Online
================================================================
]]--

"""

@bot.event
async def on_ready():
    logger.info(f'✅ Bot {bot.user.name} (ID: {bot.user.id}) is online!')
    logger.info(f'🔐 SANZZLUA Obfuscator ready!')
    logger.info(f'📡 Connected to {len(bot.guilds)} server(s)')
    
    try:
        synced = await bot.tree.sync()
        logger.info(f'⚡ Synced {len(synced)} slash command(s)')
    except Exception as e:
        logger.error(f'❌ Error syncing commands: {e}')

    # Set status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🔒 /obfuscate | SANZZLUA"
        )
    )

@bot.tree.command(
    name="obfuscate",
    description="🔒 Obfuscate file Lua dengan Level 10 Anti-AI Protection"
)
@app_commands.describe(
    file="Upload file .lua yang akan di-obfuscate",
    level="Level obfuscation (1-10, default: 10)"
)
async def obfuscate_command(
    interaction: discord.Interaction,
    file: discord.Attachment,
    level: int = 10
):
    await interaction.response.defer(thinking=True)
    
    try:
        # Validasi file extension
        if not file.filename.lower().endswith(('.lua', '.luau', '.txt')):
            await interaction.followup.send(
                "❌ **Error**: File harus berformat `.lua`, `.luau`, atau `.txt`",
                ephemeral=True
            )
            return
        
        # Validasi ukuran file (max 8MB)
        if file.size > 8 * 1024 * 1024:
            await interaction.followup.send(
                "❌ **Error**: Ukuran file maksimal 8MB",
                ephemeral=True
            )
            return
        
        # Validasi level
        if level < 1 or level > 10:
            level = 10
        
        logger.info(f'Processing file: {file.filename} ({file.size} bytes) - Level {level}')
        
        # Baca konten file
        lua_code = await file.read()
        lua_code = lua_code.decode('utf-8', errors='ignore')
        
        if not lua_code.strip():
            await interaction.followup.send(
                "❌ **Error**: File kosong atau tidak valid",
                ephemeral=True
            )
            return
        
        # Proses obfuscation
        obfuscator = LuaObfuscator(level=level)
        obfuscated_code = obfuscator.obfuscate(lua_code)
        
        # Tambahkan header
        final_code = HEADER + obfuscated_code
        
        # Buat file output
        output_filename = f"obf_{file.filename}"
        output_file = io.BytesIO(final_code.encode('utf-8'))
        output_file.seek(0)
        
        # Hitung stats
        original_size = len(lua_code)
        obfuscated_size = len(final_code)
        compression_ratio = (obfuscated_size / original_size) * 100 if original_size > 0 else 0
        
        # Buat embed
        embed = discord.Embed(
            title="🔒 SANZZLUA Obfuscator",
            description="✅ **File berhasil di-obfuscate!**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📄 File Info",
            value=f"**Original:** `{file.filename}`\n**Output:** `{output_filename}`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Protection Level",
            value=f"**Level:** {level}/10\n"
                  f"{'🔥' * level} {'⚪' * (10 - level)}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Original:** {original_size:,} bytes\n"
                  f"**Obfuscated:** {obfuscated_size:,} bytes\n"
                  f"**Ratio:** {compression_ratio:.1f}%",
            inline=True
        )
        
        # Tampilkan fitur berdasarkan level
        features = []
        if level >= 1:
            features.append("✅ Minification")
        if level >= 3:
            features.append("✅ Variable Randomization")
        if level >= 5:
            features.append("✅ String Encoding")
        if level >= 7:
            features.append("✅ Control Flow Obfuscation")
        if level >= 8:
            features.append("✅ Anti-Tamper")
        if level >= 9:
            features.append("✅ Multiple Loadstring Layers")
        if level >= 10:
            features.append("✅ VM Layer + Compression")
        
        embed.add_field(
            name="🔐 Active Protections",
            value="\n".join(features),
            inline=False
        )
        
        embed.set_footer(
            text=f"SANZZLUA Obfuscator | Requested by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890.png")  # Optional
        
        # Kirim hasil
        await interaction.followup.send(
            embed=embed,
            file=discord.File(output_file, filename=output_filename)
        )
        
        logger.info(f'Successfully obfuscated {file.filename} for {interaction.user.name}')
        
    except UnicodeDecodeError:
        await interaction.followup.send(
            "❌ **Error**: File tidak dapat dibaca. Pastikan file adalah text file yang valid.",
            ephemeral=True
        )
    except Exception as e:
        logger.error(f'Error in obfuscate command: {e}', exc_info=True)
        await interaction.followup.send(
            f"❌ **Error**: Terjadi kesalahan saat memproses file.\n{str(e)}",
            ephemeral=True
        )

@bot.tree.command(
    name="help",
    description="📚 Informasi dan panduan penggunaan SANZZLUA Obfuscator"
)
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 SANZZLUA Obfuscator - Help",
        description="**Bot untuk obfuscate file Lua dengan proteksi tingkat tinggi**\n"
                    "File yang sudah di-obfuscate **tetap bisa dijalankan** di semua platform Lua!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🔧 Commands",
        value="• `/obfuscate <file> [level]` - Obfuscate file Lua\n"
              "• `/help` - Tampilkan panduan ini\n"
              "• `/info` - Informasi bot dan statistik",
        inline=False
    )
    
    embed.add_field(
        name="🎚️ Obfuscation Levels",
        value="**Level 1-3:** Basic (Minify + Rename)\n"
              "**Level 4-6:** Medium (+ String Encoding)\n"
              "**Level 7-9:** High (+ Control Flow + Anti-Tamper)\n"
              "**Level 10:** Maximum (+ VM Layer + Compression)",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Fitur Proteksi",
        value="✅ **Level 10 Anti-AI** - Sangat sulit di-reverse\n"
              "✅ **Anti-Tamper** - Deteksi modifikasi runtime\n"
              "✅ **Multiple Loadstring** - 3-layer encoding\n"
              "✅ **String Encryption** - XOR + Base64 multi-layer\n"
              "✅ **Control Flow** - State machine obfuscation\n"
              "✅ **VM Layer** - Virtual machine execution\n"
              "✅ **Compression** - Zlib compression\n"
              "✅ **Junk Code** - Anti-pattern recognition",
        inline=False
    )
    
    embed.add_field(
        name="📖 Cara Penggunaan",
        value="1. Gunakan command `/obfuscate`\n"
              "2. Upload file `.lua` Anda\n"
              "3. Pilih level obfuscation (1-10)\n"
              "4. Tunggu proses selesai\n"
              "5. Download file hasil obfuscate\n"
              "6. File siap digunakan!",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Catatan Penting",
        value="• File output **kompatibel** dengan semua Lua runtime\n"
              "• Support: Lua 5.1, 5.2, 5.3, 5.4, LuaJIT, Luau (Roblox)\n"
              "• Maksimal ukuran file: **8MB**\n"
              "• Format: `.lua`, `.luau`, `.txt`",
        inline=False
    )
    
    embed.set_footer(text="SANZZLUA Obfuscator | Runtime Polymorphic | High Entropy")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="info",
    description="ℹ️ Informasi tentang bot dan statistik"
)
async def info_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="ℹ️ SANZZLUA Obfuscator Info",
        description="**Professional Lua Obfuscator Bot**",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="📊 Bot Stats",
        value=f"**Servers:** {len(bot.guilds)}\n"
              f"**Users:** {sum(g.member_count for g in bot.guilds)}\n"
              f"**Latency:** {round(bot.latency * 1000)}ms",
        inline=True
    )
    
    embed.add_field(
        name="🔧 Technical",
        value=f"**Python:** 3.11\n"
              f"**Discord.py:** 2.3.2\n"
              f"**Status:** 🟢 Online",
        inline=True
    )
    
    embed.add_field(
        name="🌐 Links",
        value="**GitHub:** [Repository](https://github.com/yourusername/sanzzlua)\n"
              "**Support:** Join support server\n"
              "**Deploy:** Railway + GitHub",
        inline=False
    )
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

# Error handlers
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error(f'Command error: {error}')

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f'Event error in {event}', exc_info=True)

# Run bot
def main():
    token = Config.DISCORD_TOKEN
    if not token:
        logger.error("❌ DISCORD_TOKEN tidak ditemukan! Set environment variable DISCORD_TOKEN")
        return
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid token! Periksa DISCORD_TOKEN Anda")
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main()
  
