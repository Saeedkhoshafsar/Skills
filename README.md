# 🧠 Skills — سیستم مدیریت هوشمند اسکیل‌ها

> کاربر فقط **SMART** را فعال می‌کند؛ بقیه‌ی اسکیل‌ها را SMART بر اساس فاز پروژه انتخاب و **on-demand از گیت‌هاب** نصب می‌کند — هیچ اسکیلی الکی فضای پروژه را نمی‌گیرد.

## 🌳 نقشه‌ی ریپو

```
Skills/
├── .claude-plugin/
│   └── marketplace.json ←── 🛒 کاتالوگ پلاگین (نصب مستقیم با /plugin در Claude Code)
├── README.md ←──────────── همین فایل
├── SKILLS_CATALOG.md ←──── کاتالوگ ۴۰ اسکیل بررسی‌شده (منبع تصمیم SMART)
└── skills/            ←─── هر اسکیل = یک پلاگین (SKILL.md + .claude-plugin/plugin.json)
    ├── smart/ ←─────────── 🧠 اسکیل مادر (مدیر اسکیل‌ها)
    │   ├── SKILL.md            چرخه: سنجش → تشخیص فاز → انتخاب → نصب → گزارش درختی
    │   └── scripts/
    │       └── fetch-skill.sh  دانلود تک‌اسکیل با sparse-checkout (تست‌شده ✅)
    ├── project-planner/ ←── 📋 پلن‌ساز (مصاحبه + ۱۳ لایه + PLAN.md اتمی)
    ├── project-memory/ ←─── 💾 حافظه‌ی پروژه (STATE.md — ضد قطعی و فراموشی)
    ├── step-pilot/ ←─────── ✈️ اجرای استپ‌به‌استپ (تست + Verify هر استپ)
    ├── debug-detective/ ←── 🕵️ دیباگ سیستماتیک (بازتولید → ریشه → فیکس → رگرسیون)
    └── security-check/ ←─── 🔐 ممیزی امنیتی قبل از انتشار (سکرت، وابستگی، Auth، ...)
```

## 🛒 نصب روی Claude Code (روش اصلی — پلاگین مارکت‌پلیس)

```bash
# 1. افزودن مارکت‌پلیس (یک‌بار):
claude plugin marketplace add Saeedkhoshafsar/Skills
#   یا داخل جلسه:  /plugin marketplace add Saeedkhoshafsar/Skills

# 2. نصب اسکیل مادر (کافی است — بقیه را خودش مدیریت می‌کند):
claude plugin install smart@saeed-skills

# (اختیاری) نصب مستقیم بقیه:
claude plugin install project-planner@saeed-skills
claude plugin install project-memory@saeed-skills
claude plugin install step-pilot@saeed-skills
claude plugin install debug-detective@saeed-skills
claude plugin install security-check@saeed-skills

# بروزرسانی بعداً:
claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills
```

> ⚠️ اگر قبلاً ارور `Marketplace file not found at ...\.claude-plugin\marketplace.json` گرفتی،
> اول مارکت‌پلیس خراب را پاک کن و دوباره اضافه کن:
> ```bash
> claude plugin marketplace remove Saeedkhoshafsar-Skills   # یا نامی که قبلاً ثبت شده
> claude plugin marketplace add Saeedkhoshafsar/Skills
> ```
> این ریپو حالا فایل `.claude-plugin/marketplace.json` را در ریشه دارد — ارور رفع شده است. ✅

## 🚀 استفاده بدون مارکت‌پلیس (روش دستی — هر ایجنتی)

```bash
# 1. فقط SMART را به پروژه ببر:
mkdir -p .claude/skills
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/Saeedkhoshafsar/Skills.git /tmp/sk
git -C /tmp/sk sparse-checkout set skills/smart
cp -r /tmp/sk/skills/smart .claude/skills/ && rm -rf /tmp/sk

# 2. به ایجنت بگو: «اسکیل smart را فعال کن»
#    بقیه را خودش تشخیص می‌دهد و نصب می‌کند.
```

## 🔄 چرخه‌ی زندگی پروژه با SMART

```
پروژه خالی ──smart──► project-planner (پلن + مصاحبه)
     │
پلن آماده ──smart──► project-memory + step-pilot (حافظه + استپ‌ها)
     │
وسط توسعه ──smart──► sparc-methodology + verification-quality (از گیت‌هاب ⬇)
     │          └─ باگ/ارور تکراری؟ ──► debug-detective 🕵️
     │
آماده انتشار ──smart──► security-check 🔐 (دروازه!) + github-release-management + hooks-automation (⬇)
     │
نگهداری ──smart──► github-project-management (⬇)
```

## 📦 منابع اسکیل (fetch-skill.sh از این‌ها می‌کِشد)

| منبع | تعداد | محتوا |
|---|---|---|
| همین ریپو `skills/` | ۶ | smart، planner، memory، step-pilot، debug-detective، security-check |
| `Saeedkhoshafsar/ruflo` → `.claude/skills` | ۳۹ | حافظه، گیت‌هاب، swarm، کیفیت و... (کاتالوگ را ببین) |
| `Saeedkhoshafsar/claude-plugins-official` | ۱ | claude-automation-recommender |

جزئیات و سطح‌بندی هر ۴۰ اسکیل → [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)
