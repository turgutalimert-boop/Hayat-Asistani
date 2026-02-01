import discord, os, datetime, pytz, asyncio
from discord.ext import commands
import google.generativeai as genai

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-lite")

chat_history = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Karakter: Vakur ve Sade Akşemsettin
PERSONALITY = (
    "Sen bir Türk-İslam alimisin. Akşemsettin gibi vakur ve bilge bir duruşun var. "
    "Mert Bey'e hitap ederken sadece 'Beyefendi' veya 'Efendim' tabirlerini kullan. "
    "Asla 'Sultanım', 'Şahım' gibi abartılı ve yalaka duran hitaplara girme. "
    "Laf kalabalığından kaçın. Sözün öz, hikmetli ve ciddi olsun. "
    "Bir hoca vakarında, doğrudan meseleye odaklanan cevaplar ver."
)

@bot.event
async def on_ready():
    print("Hayati (Vakur Alim) Görev Başında!")
    await bot.tree.sync()

async def hayati_cevap_ver(channel_id, soru):
    try:
        bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
        if channel_id not in chat_history:
            chat_history[channel_id] = []
        
        past_context = "\n".join(chat_history[channel_id][-6:])
        full_prompt = f"{PERSONALITY}\nBugün: {bugun}\nGeçmiş Muhabbet:\n{past_context}\nBeyefendi: {soru}"
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: ai_model.generate_content(full_prompt))
        
        chat_history[channel_id].append(f"Efendim: {soru}")
        chat_history[channel_id].append(f"Hayati: {response.text}")
        
        return response.text
    except Exception as e:
        return f"Efendim, bir kusur hasıl oldu: {e}"

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if "hayati" in message.content.lower() or bot.user.mentioned_in(message):
        async with message.channel.typing():
            cevap = await hayati_cevap_ver(message.channel.id, message.content)
            await message.reply(cevap)

@bot.tree.command(name="hayati", description="Bilgeye danışın")
async def hayati_slash(interaction: discord.Interaction, soru: str):
    await interaction.response.defer(thinking=True)
    cevap = await hayati_cevap_ver(interaction.channel_id, soru)
    await interaction.followup.send(cevap)

bot.run(TOKEN)
