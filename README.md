# 🧠 Skills — سیستم مدیریت هوشمند اسکیل‌ها

> کاربر فقط **SMART** را فعال می‌کند؛ بقیه‌ی اسکیل‌ها را SMART بر اساس فاز پروژه انتخاب و **on-demand از گیت‌هاب** نصب می‌کند — هیچ اسکیلی الکی فضای پروژه را نمی‌گیرد.

## 🌳 نقشه‌ی ریپو

```
Skills/
├── README.md ←──────────── همین فایل
├── SKILLS_CATALOG.md ←──── کاتالوگ ۴۰ اسکیل بررسی‌شده (منبع تصمیم SMART)
└── skills/
    ├── smart/ ←─────────── 🧠 اسکیل مادر (مدیر اسکیل‌ها)
    │   ├── SKILL.md            چرخه: سنجش → تشخیص فاز → انتخاب → نصب → گزارش درختی
    │   └── scripts/
    │       └── fetch-skill.sh  دانلود تک‌اسکیل با sparse-checkout (تست‌شده ✅)
    ├── project-planner/ ←── 📋 پلن‌ساز (مصاحبه + ۱۳ لایه + PLAN.md اتمی)
    ├── project-memory/ ←─── 💾 حافظه‌ی پروژه (STATE.md — ضد قطعی و فراموشی)
    └── step-pilot/ ←─────── ✈️ اجرای استپ‌به‌استپ (تست + Verify هر استپ)
```

## 🚀 استفاده در یک پروژه‌ی جدید

```bash
# 1. فقط SMART را به پروژه ببر:
mkdir -p .claude/skills
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/tivanmelhotra-creator/Skills.git /tmp/sk
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
     │
آماده انتشار ──smart──► github-release-management + hooks-automation (⬇)
     │
نگهداری ──smart──► github-project-management (⬇)
```

## 📦 منابع اسکیل (fetch-skill.sh از این‌ها می‌کِشد)

| منبع | تعداد | محتوا |
|---|---|---|
| همین ریپو `skills/` | ۴ | smart، planner، memory، step-pilot |
| `Saeedkhoshafsar/ruflo` → `.claude/skills` | ۳۹ | حافظه، گیت‌هاب، swarm، کیفیت و... (کاتالوگ را ببین) |
| `Saeedkhoshafsar/claude-plugins-official` | ۱ | claude-automation-recommender |

جزئیات و سطح‌بندی هر ۴۰ اسکیل → [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)
