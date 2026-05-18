import csv
import random

# --- VARIABLES FOR RANDOMIZATION ---
banks = ["Maybank", "CIMB", "RHB", "Public Bank", "Hong Leong", "AmBank", "Bank Islam"]
companies = ["Shopee", "Lazada", "Touch 'n Go", "Grab", "Foodpanda", "TNB", "Celcom", "Maxis", "Digi", "U Mobile"]
agencies = ["LHDN", "PDRM", "SPRM", "KWSP", "BNM", "JPJ", "Mahkamah"]
names = ["Ali", "Ahmad", "Muthu", "Chong", "Siti", "Fatimah", "Sarah", "Kevin", "Amir"]
amounts = [10, 50, 100, 300, 500, 1000, 3000, 5000, 10000, 50000]
otps = [random.randint(100000, 999999) for _ in range(100)]

# --- TEMPLATES ---
spam_templates = [
    "{agency} Notice: You have unpaid penalty of RM{amount}. Pay immediately via this link to avoid arrest.",
    "RM0.00 {bank}: Your account is blocked due to suspicious transfer of RM{amount}. Verify OTP here.",
    "Tahniah! Nombor anda menang cabutan bertuah {company} bernilai RM{amount}. Sila bayar processing fee.",
    "Your {company} parcel is stuck at customs. Please pay clearance fee of RM{amount} immediately.",
    "Hello I am HR from {company}. We offer part time job clicking ads. Salary RM{amount} daily. Reply YES.",
    "{agency}: Waran tangkap dikeluarkan atas nama anda kerana kes pengubahan wang haram. Hubungi pegawai.",
    "Bantuan Tunai Rahmah RM{amount} sedia untuk ditebus. Klik pautan rasmi {bank} ini sekarang.",
    "Your {bank} TAC is {otp}. If you did not request this, please secure your account immediately.",
    "Pinjaman peribadi lulus 100%! Pinjam RM{amount} tanpa penjamin. Blacklist CTOS CCRIS boleh mohon.",
    "RM0 {company}: Akaun e-wallet anda akan digantung dalam masa 24 jam. Kemaskini maklumat anda."
]

ham_templates = [
    "Weh jom makan kat mamak, aku belanja hari ni.",
    "Bro, tolong transfer aku RM{amount} dulu, esok gaji aku bayar balik.",
    "Your {company} driver is arriving in 5 mins. Please meet at the lobby.",
    "Dah siap assignment Prof belum? Aku pening gila babi coding ni.",
    "Happy Birthday {name}! Moga dimurahkan rezeki selalu.",
    "Tolong belikan nasi lemak 2 bungkus, nanti aku bayar.",
    "Are we still meeting at the library tomorrow at 10am?",
    "My {company} app is lagging, can you check if the server is down?",
    "I just bought the new keyboard from {company}, finally arrived!",
    "Kau kat mana? Kitorang dah sampai kelas ni."
]

# --- GENERATION LOGIC ---
print("⚙️ Generating 10,000 rows of Malaysian SMS Data...")

dataset = []

# Generate 5,000 Spam
for _ in range(5000):
    template = random.choice(spam_templates)
    msg = template.format(
        bank=random.choice(banks),
        company=random.choice(companies),
        agency=random.choice(agencies),
        amount=random.choice(amounts),
        otp=random.choice(otps)
    )
    dataset.append(["spam", msg])

# Generate 5,000 Ham (Safe)
for _ in range(5000):
    template = random.choice(ham_templates)
    msg = template.format(
        bank=random.choice(banks),
        company=random.choice(companies),
        name=random.choice(names),
        amount=random.choice(amounts)
    )
    dataset.append(["ham", msg])

# Shuffle the dataset so spam and ham are mixed randomly
random.shuffle(dataset)

# --- WRITE TO CSV ---
file_name = "dataset/malaysia_spam_10k.csv"
with open(file_name, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["v1", "v2"])  # Column headers
    writer.writerows(dataset)

print(f"✅ SUCCESS! 10,000 rows saved to '{file_name}'.")