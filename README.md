# Thai Astrology Skill (โหราศาสตร์ไทย)

A [Claude Code](https://claude.com/claude-code) skill for Thai astrology — birth chart casting, fortune-telling, auspicious naming (ทักษา), and time selection (ฤกษ์) — using **Swiss Ephemeris** for professional-grade planetary calculations.

> Skill สำหรับ Claude Code เพื่อทำนายดวงตามหลักโหราศาสตร์ไทย ผูกดวง ตั้งชื่อมงคล และเลือกฤกษ์ โดยใช้ Swiss Ephemeris คำนวณตำแหน่งดาวอย่างแม่นยำ

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Powered by uv](https://img.shields.io/badge/powered%20by-uv-DE5FE9)](https://github.com/astral-sh/uv)

---

## ✨ Features

- 🌟 **ผูกดวง (Birth Chart Casting)** — คำนวณตำแหน่งดาว 10 ดวง + ลัคนา + ภพ 12 ด้วย Swiss Ephemeris
- 📝 **ตั้งชื่อมงคล (Auspicious Naming)** — วิเคราะห์อักษรไทยตามระบบทักษาปกรณ์ 8 หมวด
- 🗓️ **เลือกฤกษ์ (Auspicious Time)** — แนะนำวันมงคลตามวัตถุประสงค์ (แต่งงาน ขึ้นบ้าน เปิดร้าน ฯลฯ)
- 🔮 **พยากรณ์รายวัน/รายปี** — เทียบดวงจรกับดวงกำเนิดเพื่อชี้เหตุการณ์
- 🇹🇭 **Thai-first** — output, scripts, references, and reasoning all in Thai
- 💬 **Smart prompting** — uses `AskUserQuestion` to gather missing context interactively

---

## 📦 Installation

### Prerequisites

- **[uv](https://github.com/astral-sh/uv)** — modern Python package manager
- **Claude Code** — [download here](https://claude.com/claude-code)

### Quick install (uv)

```bash
# Clone the repo
git clone https://github.com/premchotipanit/thai-astrology-skill.git
cd thai-astrology-skill

# Install dependencies with uv
uv sync
```

### As a Claude Code plugin marketplace (recommended for teams)

This repo is a Claude Code plugin marketplace — teammates can install the skill with one command:

```bash
# 1) Register the marketplace (run once per machine)
/plugin marketplace add batprem/thai-astrology-skill

# 2) Install the skill
/plugin install thai-astrology@thai-astrology-skill
```

After install, Claude Code triggers the skill automatically when you mention โหราศาสตร์, ดูดวง, ผูกดวง, ลัคนา, ราศี, ฤกษ์, ทักษา, or just give a birthdate.

### As a plain Claude Code skill (alt — single user)

Copy or symlink the skill folder into Claude Code's skills directory:

```bash
# Project-level (in your project)
mkdir -p .claude/skills
ln -s "$(pwd)/skills/thai-astrology" .claude/skills/thai-astrology

# OR global (all projects)
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/thai-astrology" ~/.claude/skills/thai-astrology
```

---

## 🚀 Usage

### As Claude Code skill (recommended)

ในช่อง Claude Code พิมพ์ภาษาไทยตามธรรมชาติ ตัวอย่าง:

```
อยากดูดวง เกิด 15 มกราคม 2535 เวลา 8:30 ที่กรุงเทพ
```

```
ลูกชายเกิดวันอังคาร อยากตั้งชื่อว่า "ภูมิ" ดีไหม
```

```
อยากแต่งงานเดือนตุลาคม 2569 ดูฤกษ์ดีให้หน่อย
```

Skill จะอ่าน `SKILL.md` → ขอข้อมูลที่ขาดผ่าน `AskUserQuestion` → รัน scripts → ตีความ → ตอบเป็นภาษาไทย พร้อม disclaimer

### As CLI tools

หลังจาก `uv sync` แล้ว สามารถรัน scripts ตรง ๆ ได้:

```bash
# 1. ผูกดวง
uv run python skills/thai-astrology/scripts/cast_chart.py --date 2535-01-15 --time 08:30 --place กรุงเทพ

# 2. วิเคราะห์ทักษา
uv run python skills/thai-astrology/scripts/taksa.py --day อังคาร --name ภูมิ

# 3. หาฤกษ์มงคล
uv run python skills/thai-astrology/scripts/auspicious_time.py --from 2569-10-01 --to 2569-10-31 --purpose แต่งงาน --top 5
```

---

## 📂 Project Structure

```
thai-astrology-skill/             # ← Claude Code plugin marketplace root
├── .claude-plugin/
│   ├── marketplace.json          # marketplace metadata
│   └── plugin.json               # plugin metadata
│
├── skills/
│   └── thai-astrology/           # ← the skill
│       ├── SKILL.md              # Skill definition + workflow + templates
│       ├── scripts/              # Python tools
│       │   ├── cast_chart.py     # ผูกดวงด้วย Swiss Ephemeris
│       │   ├── taksa.py          # วิเคราะห์ทักษา + ตั้งชื่อ
│       │   └── auspicious_time.py # หาฤกษ์มงคล
│       ├── references/           # Knowledge base (loaded on demand)
│       │   ├── bhava_meanings.md # ความหมายของภพ 12 ภพ
│       │   ├── planet_standards.md # เกษตร/อุจ/ประ/นิจ
│       │   ├── taksa_system.md   # ระบบทักษา 8 หมวด
│       │   └── aspects.md        # มุมสัมพันธ์ดาว
│       └── evals/
│           └── evals.json        # 3 test prompts + assertions
│
├── pyproject.toml                # uv/pip metadata + dependencies
├── README.md                     # คุณกำลังอ่านอยู่
└── LICENSE                       # MIT
```

---

## 🧪 Testing the skill

Eval results from initial benchmarks (with-skill vs. baseline Claude):

| Test case                              | With skill | Baseline | Δ           |
|----------------------------------------|------------|----------|-------------|
| ผูกดวงและพยากรณ์                       | **100%**   | 57.1%    | **+42.9%**  |
| วิเคราะห์ชื่อตามทักษา                  | 100%       | 100%     | 0%          |
| เลือกฤกษ์แต่งงาน                       | 100%       | 100%     | 0%          |
| **Average**                            | **100%**   | **85.7%**| **+14.3%**  |

The biggest gain is in chart casting — baseline Claude tends to **guess planetary positions incorrectly** (wrong ascendant, wrong planet rasi) when no ephemeris is available.

---

## 🌐 Languages

- **All skill outputs** are in Thai (per design)
- **Code comments** are bilingual (Thai + English)
- **Documentation** (this README, CONTRIBUTING) — bilingual

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/something`)
3. Make changes — run scripts locally to test
4. Open a Pull Request

ไม่จำเป็นต้องเชี่ยวชาญโหราศาสตร์ — bug fixes, doc improvements, additional cities/places, and test cases all welcome.

### Adding cities

Thai cities are listed in `skills/thai-astrology/scripts/cast_chart.py` (`THAI_CITIES` dict). Add new entries as `(latitude, longitude)` tuples.

### Improving interpretations

References in `skills/thai-astrology/references/*.md` are the source of truth for skill interpretations. Edit those Markdown files to refine wording.

---

## 📜 Astrological caveat

โหราศาสตร์ในวัฒนธรรมไทยเป็น **เครื่องมือชี้แนวโน้มและให้คำแนะนำ** ไม่ใช่การฟันธงชะตา การพยากรณ์ที่ skill นี้สร้างขึ้นเป็นการประยุกต์ตำราโบราณกับการคำนวณดาวสมัยใหม่ ผู้ใช้ควรพิจารณาด้วยวิจารณญาณ ไม่ควรนำไปใช้ตัดสินใจเรื่องสำคัญในชีวิต (สุขภาพ การลงทุน ความสัมพันธ์) โดยไม่ปรึกษาผู้เชี่ยวชาญในด้านนั้น ๆ ก่อน

> Astrology in Thai culture is **a guide for tendencies, not a deterministic verdict.** This skill applies traditional Thai texts to modern astronomical calculation. Users should exercise judgment and not rely on it for major life decisions (health, finance, relationships) without consulting domain experts.

---

## 🙏 Credits

- **[Swiss Ephemeris](https://www.astro.com/swisseph/)** — astronomical computation library (Astrodienst AG)
- **[pyswisseph](https://github.com/astrorigin/pyswisseph)** — Python binding for Swiss Ephemeris
- ตำราโหราศาสตร์ไทย เรียบเรียงโดย หลวงวิศาลดรุณกร (อั้น สาริกบุตร) และอื่น ๆ ที่ปรากฏใน [research-thai-astrology.md](https://github.com/premchotipanit/thai-astrology-skill)
- Built with [Claude Code](https://claude.com/claude-code) and the skill-creator skill

---

## 📄 License

MIT — see [LICENSE](LICENSE)
