# Thai Astrology Skill (โหราศาสตร์ไทย)

A [Claude Code](https://claude.com/claude-code) skill for Thai astrology — birth chart casting, fortune-telling, auspicious naming (ทักษา), and time selection (ฤกษ์).

> Skill สำหรับ Claude Code เพื่อทำนายดวงตามหลักโหราศาสตร์ไทย ผูกดวง ตั้งชื่อมงคล และเลือกฤกษ์

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Powered by uv](https://img.shields.io/badge/powered%20by-uv-DE5FE9)](https://github.com/astral-sh/uv)

---

> **Fork of [batprem/thai-astrology-skill](https://github.com/batprem/thai-astrology-skill).** This fork adds a second calculation engine, `--ayanamsa suriyayat` (สุริยยาตร์): a from-scratch port of the traditional Thai suriyayat method (ported from [kongesque/thai-astrology](https://github.com/kongesque/thai-astrology), extended to keep degree-level precision for every planet instead of just sign) — no ephemeris library required, and verified to reproduce a real Thai astrologer's traditional reading exactly (see `zodiac-system-check-natal-vs-tape.md` in the source project). The original `--ayanamsa tropical`/`lahiri` (Swiss Ephemeris `houses()`) engine is unchanged and stays available for astronomically-real reference/comparison — the two give different ascendants (they measure different things), see the "เครื่องมือคำนวณ 2 เอนจิน" section in `SKILL.md`. Birth time also still defaults to 06:00 (sunrise) when unknown, rather than blocking or guessing 06:55.

## ✨ Features

- 🌟 **ผูกดวง (Birth Chart Casting)** — คำนวณตำแหน่งดาว 10 ดวง + ลัคนา + ภพ 12 ด้วยเอนจิน 2 แบบ: สุริยยาตร์ตำราไทยดั้งเดิม (ไม่ต้องมี ephemeris) หรือ Swiss Ephemeris (ลัคนาดาราศาสตร์จริง)
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
# 1. ผูกดวง — สุริยยาตร์ตำราไทยดั้งเดิม (แนะนำ ไม่ต้องมี pyswisseph)
uv run python skills/thai-astrology/scripts/cast_chart.py --date 2535-01-15 --time 08:30 --place กรุงเทพ --ayanamsa suriyayat

# 1b. ผูกดวง — Swiss Ephemeris (ลัคนาดาราศาสตร์จริง ต้องมี pyswisseph)
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
│       │   ├── cast_chart.py     # ผูกดวง — 2 เอนจิน (suriyayat / Swiss tropical+lahiri)
│       │   ├── suriyayat_calc.py # เอนจินสุริยยาตร์ตำราไทย (ไม่พึ่ง ephemeris) ใช้โดย cast_chart.py
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

### Eval results

Initial benchmarks (with-skill vs. baseline Claude):

| Test case                              | With skill | Baseline | Δ           |
|----------------------------------------|------------|----------|-------------|
| ผูกดวงและพยากรณ์                       | **100%**   | 57.1%    | **+42.9%**  |
| วิเคราะห์ชื่อตามทักษา                  | 100%       | 100%     | 0%          |
| เลือกฤกษ์แต่งงาน                       | 100%       | 100%     | 0%          |
| **Average**                            | **100%**   | **85.7%**| **+14.3%**  |

The biggest gain is in chart casting — baseline Claude tends to **guess planetary positions incorrectly** (wrong ascendant, wrong planet rasi) when no ephemeris is available.

### Eval set

Test cases อยู่ที่ [`skills/thai-astrology/evals/evals.json`](skills/thai-astrology/evals/evals.json) — แต่ละ case มี:

- `prompt` — ข้อความที่ผู้ใช้พิมพ์ (เช่น "ดูดวงให้หน่อย เกิด 15 มกราคม 2535 …")
- `expected_output` — สิ่งที่ skill ควรทำในระดับภาพรวม
- `assertions[]` — checklist สำหรับให้คนหรือ Claude grader ตรวจคำตอบทีละข้อ

ครอบคลุม 3 สถานการณ์: ผูกดวง, วิเคราะห์ชื่อตามทักษา, เลือกฤกษ์แต่งงาน

### วิธีรัน evals

**1. แบบมือ (สั้นและตรงประเด็นที่สุด)** — เปิด Claude Code ที่โฟลเดอร์นี้ แล้ว copy `prompt` ของแต่ละ case ไปวาง ตรวจคำตอบเทียบกับ `assertions[]` ทีละข้อ

```bash
# ดู prompt + assertions ของทุก case
jq '.evals[] | {id, name, prompt, assertions}' \
  skills/thai-astrology/evals/evals.json
```

**2. แบบอัตโนมัติด้วย `skill-creator`** (แนะนำเมื่อแก้ skill แล้วอยากเทียบรอบใหม่ vs. รอบเก่า)

ใน Claude Code:

```
/skill-creator
```

แล้วบอกว่า "รัน evals สำหรับ skill thai-astrology" — skill-creator จะอ่าน `evals.json`, รัน prompts ทั้งหมดทั้งแบบ with-skill และ baseline, เก็บผลใน `thai-astrology-workspace/iteration-N/` แล้วสร้าง eval viewer (HTML) ให้รีวิว

**3. Trigger eval (description ดีพอจน Claude เรียก skill เองหรือยัง)**

```bash
python ~/.claude/skills/skill-creator/scripts/run_eval.py \
  --eval-set skills/thai-astrology/evals/evals.json \
  --skill-path skills/thai-astrology \
  --runs-per-query 3 \
  --verbose
```

แสดง trigger rate ของแต่ละ prompt — ถ้าต่ำกว่า 0.5 แปลว่า description ใน `SKILL.md` ยังไม่ดึงดูดพอ ควรปรับคีย์เวิร์ด

### เพิ่ม test case ใหม่

เปิด `skills/thai-astrology/evals/evals.json` แล้ว append entry ใหม่เข้าใน `evals[]` ตาม schema เดิม (`id`, `name`, `prompt`, `expected_output`, `assertions[]`, `files[]`) — ไม่มี id ใหม่จะ collide เพราะรันด้วย index

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


## โหมดเทียบสองระบบ (`--compare`) — เพิ่มใน 0.2.0

```bash
python skills/thai-astrology/scripts/cast_chart.py \
  --date 2541-01-05 --time 22:50 --lat 18.29 --lon 99.49 --compare
```

พิมพ์ผลสายนะ (ทรอปิคัล) กับนิรายนะ (Lahiri) เคียงกัน พร้อมค่า ayanamsa ณ วันเกิด
ฤกษ์และเจ้าฤกษ์ ตรียางค์และเจ้าตรียางค์ ดิถี อัตราลัคนาเดินเป็นองศาต่อนาที
และระยะจากลัคนาถึงเส้นแบ่งราศีคิดเป็นนาทีของเวลาเกิด

เพิ่ม `--format json` ถ้าต้องการโครงสร้างข้อมูลแทนตาราง

โหมดปกติ (ไม่ใส่ `--compare`) เพิ่มฟิลด์ `ฤกษ์` `ตรียางค์` `ดิถี` `ayanamsa`
และ `julian_day_ut` เข้าไปใน JSON ด้วย ฟิลด์เดิมทั้งหมดยังอยู่ครบ
