import discord, os, datetime, pytz, asyncio
from discord.ext import commands
import google.generativeai as genai

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Hafıza için sözlük (Her kanalın kendi geçmişi olacak)
chat_history = {}

KRITIK_TARIHLER = {
    "Vietnam Vizesi": "2026-05-15",
    "Kiz Arkadasimin Dogum Gunu": "2026-08-20"
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

PERSONALITY = (
    "Sen Mert abinin sadık asistanı Hayati'sin. "
    "Karakterin: Bir Türk-İslam bilgini, alim. "
    "Üslubun: Vakur, hikmetli ve saygılı. Cümlelerinde 'Mert abi' hitabını eksik etme. "
    "Özellik: Geçmiş konuşmaları hatırla ve ona göre süreklilik sağla."
)

@bot.event
async def on_ready():
    print("Hayati 2026 (Hafıza Ünitesi Devrede) Aktif!")
    await bot.tree.sync()

async def hayati_cevap_ver(channel_id, soru):
    try:
        bugun = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
        
        # Hafıza yönetimi
        if channel_id not in chat_history:
            chat_history[channel_id] = []
        
        # Geçmişi prompt'a ekle
        past_context = "\n".join(chat_history[channel_id][-10:]) # Son 10 mesajı hatırlar
        full_prompt = f"{PERSONALITY}\nBugün: {bugun}\nGeçmiş Muhabbet:\n{past_context}\nMert abi: {soru}"
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: ai_model.generate_content(full_prompt))
        
        # Yeni cevabı hafızaya ekle
        chat_history[channel_id].append(f"Mert abi: {soru}")
        chat_history[channel_id].append(f"Hayati: {response.text}")
        
        return response.text
    except Exception as e:
        return f"Mert abi, zihnim bulandı, hatamı bağışla: {e}"

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if "hayati" in message.content.lower() or bot.user.mentioned_in(message):
        async with message.channel.typing():
            cevap = await hayati_cevap_ver(message.channel.id, message.content)
            await message.reply(cevap)

@bot.tree.command(name="hayati", description="Bilge Hayati'ye danış")
async def hayati_slash(interaction: discord.Interaction, soru: str):
    await interaction.response.defer(thinking=True)
    cevap = await hayati_cevap_ver(interaction.channel_id, soru)
    await interaction.followup.send(cevap)

bot.run(TOKEN)
