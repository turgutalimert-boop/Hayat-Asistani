import discord, os  # <--- Buraya os ekledik
from discord.ext import tasks, commands
import datetime, random, requests, pytz

# --- AYARLAR ---
TOKEN = os.getenv('DISCORD_TOKEN') # <--- İçini boşalttık, Railway'den alacak
WEATHER_API_KEY = os.getenv('WEATHER_KEY') # <--- İçini boşalttık
CITY = 'Nha Trang'
HEDEF_KANAL_ADI = 'genel' 

# --- 100 MADDELİK SABIR, KİBİR VE TEVAZU KÜTÜPHANESİ ---
MANEVI_DESTEK = [
    "Şüphesiz Allah sabredenlerle beraberdir. (Bakara, 153)", "Yeryüzünde böbürlenerek yürüme. (İsrâ, 37)",
    "Allah, büyüklük taslayanları sevmez. (Nahl, 23)", "Sabret! Senin sabrın ancak Allah'ın yardımı iledir. (Nahl, 127)",
    "Kalbinde zerre kadar kibir bulunan kimse cennete giremez. (Hadis-i Şerif)", "Tevazu göstereni Allah yüceltir, kibirleneni Allah alçaltır. (Hadis-i Şerif)",
    "Zorluğun yanında bir kolaylık vardır. (İnşirah, 5)", "Güzel bir sabırla sabret. (Meâric, 5)",
    "Sabredenlere mükafatları hesapsız ödenecektir. (Zümer, 10)", "Kibir, hakkı reddetmek ve insanları hor görmektir. (Hadis-i Şerif)",
    "Ey iman edenler! Sabredin, sebat gösterin. (Âl-i İmrân, 200)", "Sabır, ferahlığın anahtarıdır. (Hadis-i Şerif)",
    "Kim sabrederse Allah ona dayanma gücü verir. (Hadis-i Şerif)", "Allah sabredenleri sever. (Âl-i İmrân, 146)",
    "Sabır, imanın yarısıdır. (Hadis-i Şerif)", "En büyük günah, kendini günahsız görmektir. (Hz. Ali)",
    "Sabır boyun eğmek değil, mücadele etmektir. (Hz. Ali)", "Kibir, bilgisizliğin meyvesidir.",
    "Alçak gönüllü olan, yüksekleri fetheder.", "Makamın yükseldikçe tevazun artsın.",
    "Sabır, beklemeyi bilmek değil, beklerken doğru duruş sergilemektir.", "Kibir, şeytanın mirasıdır.",
    "Senin için yazılmış olan seni bulacaktır, sabret.", "Tevazu seni korur, kibir ise hedef tahtası yapar.",
    "Sabır ruhun cilası, kibir ise pasıdır.", "Gecenin en karanlık anı, sabaha en yakın olanıdır. Sabret.",
    "Kibir, akıllı adamın aptallığıdır.", "Sabır, musibetlerin ilacıdır.",
    "Tevazu, asaletin süsüdür.", "Sabır, aklın yarısıdır.",
    "Kibirli gönül, Allah'ın nurundan mahrum kalır.", "Sabır, imanın başıdır.",
    "Tevazu gösteren, her gönülde taht kurar.", "Sabır, karanlıkları aydınlatan bir meşaledir.",
    "Allah, sabredeni aziz, kibirleneni rezil eder.", "Sabır bineklerin en hayırlısıdır.",
    "Kibirli insan, aynaya bakınca sadece kendini görür.", "Acele şeytandan, sabır Rahman'dandır.",
    "Tevazu ile yükselen, asla düşmez.", "Sabır, kurtuluşun anahtarıdır.",
    "Kibir, doğruluğun önündeki en büyük engeldir.", "Sabırla koruk helva olur.",
    "Kibirli bakış, hakikati göremez.", "Mütevazı yaşa ki başın göğe ersin.",
    "Sabır, iman ağacının köküdür.", "Kibir, insanın içindeki boşluğu gizleme çabasıdır.",
    "Sabır, ruhun sükunetidir.", "Alçak gönüllülük dervişin hırkasıdır.",
    "Sabır, insanın sırtındaki dağı taşımasına yardım eder.", "Kibrin bittiği yerde huzur başlar.",
    "Sabır, en büyük zırhtır.", "Tevazu, her hayrın anahtarıdır.",
    "Kibirli ağaç ilk fırtınada kırılır.", "Sabır, her zorluğun sonundaki ödüldür.",
    "Mümin, kibirden arınmış bir kalp taşımalıdır.", "Sabır, sessiz bir feryattır.",
    "Kibir, başarının en büyük düşmanıdır.", "Tevazu, kalbin ziynetidir.",
    "Sabır, umudun diğer adıdır.", "Kibir, cehaletin en belirgin işaretidir.",
    "Sabretmek, şikayet etmeden katlanmaktır.", "Tevazu gösteren, Allah katında değer kazanır.",
    "Kibir, insanın kendi kendine kurduğu bir tuzaktır.", "Sabır, zamanın en büyük ilacıdır.",
    "Mütevazı olanın dostu çok olur.", "Kibir, ruhun ağır yüküdür.",
    "Sabır, Allah'a teslimiyettir.", "Tevazu, kibirden kurtuluş yoludur.",
    "Kibirli olan, gerçek dost edinemez.", "Sabret ki her şey vaktinde güzelleşsin.",
    "Alçak gönüllülük, bilgeliğin başlangıcıdır.", "Kibir, hakikate karşı körlüktür.",
    "Sabır, kalbin sebatıdır.", "Tevazu, insanı insan yapan değerdir.",
    "Kibir, şeytanın ilk günahıdır.", "Sabır, zaferin müjdecisidir.",
    "Mütevazı bir hayat, en büyük zenginliktir.", "Kibir, kırılgandır; tevazu ise sarsılmaz.",
    "Sabır, dayanıklılık sanatıdır.", "Tevazu, erdemin temelidir.",
    "Kibirli insan, öğrenmeye kapalıdır.", "Sabretmek, meyvenin olgunlaşmasını beklemektir.",
    "Tevazu, ruhun olgunluğunu gösterir.", "Kibir, başkalarını küçümseyerek kendini büyük sanmaktır.",
    "Sabır, zorlukların üstesinden gelme gücüdür.", "Tevazu, samimiyetin kardeşidir.",
    "Kibir, kalbi katılaştırır.", "Sabır, huzura giden yoldur.",
    "Mütevazı olan, her zaman kazanır.", "Kibirli bir ruh, asla doyum bulamaz.",
    "Sabır, hayatın fırtınalarına karşı dayanmaktır.", "Tevazu, büyüklüğün şanındandır.",
    "Kibir, bir perde gibi gerçeği örter.", "Sabır, her kapıyı açan anahtardır.",
    "Tevazu gösteren, saygı görür.", "Kibir, yalnızlığa mahkum eder.",
    "Sabret, nasibin seni bulur.", "Tevazu, içsel huzurun kaynağıdır.",
    "Kibir, egoizmin meyvesidir.", "Sabır ve tevazu, kamil insanın iki kanadıdır."
]

class SunucuAsistani(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.rutin_kontrol.start()

    async def on_ready(self):
        print(f'✅ {self.user} aktif!')

    def get_weather(self):
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=tr"
            data = requests.get(url).json()
            return {"temp": data['main']['temp'], "desc": data['weather'][0]['description'], "main": data['weather'][0]['main']}
        except: return None

    @tasks.loop(minutes=1)
    async def rutin_kontrol(self):
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.datetime.now(tz)
        current_time = now.strftime("%H:%M")

        for guild in self.guilds:
            channel = discord.utils.get(guild.text_channels, name=HEDEF_KANAL_ADI)
            if not channel: continue

            # 1. Sabah Raporu
            if current_time == "08:30":
                w = self.get_weather()
                if w:
                    msg = f"☀️ **Hayırlı Sabahlar!**\nBugün hava {w['temp']}°C ve {w['desc']}."
                    await channel.send(msg)

            # 2. Saatlik Su Hatırlatıcı (09:00 - 22:00 arası her saat başı)
            if now.minute == 0 and 9 <= now.hour <= 22:
                await channel.send("💧 **Saatlik Su Hatırlatması:** Abi sağlığın için bir bardak su içmeyi unutma.")

            # 3. Akşam Tefekkürü
            if current_time == "21:30":
                soz = random.choice(MANEVI_DESTEK)
                await channel.send(f"📖 **Günün Tefekkürü:**\n\n> *{soz}*")

bot = SunucuAsistani()
bot.run(TOKEN)
