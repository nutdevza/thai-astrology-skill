"""สุริยยาตร์ (Suriyayat) — คำนวณดวงตามตำราโหราศาสตร์ไทยดั้งเดิม ไม่พึ่ง ephemeris ใด ๆ

พอร์ตจาก kongesque/thai-astrology (TypeScript, dist/engine/astro-calculation.js) มาเป็น
Python บรรทัดต่อบรรทัด แต่มีจุดต่างจากต้นฉบับ 2 จุด:

1. ห้องสมุดต้นทางปัดตำแหน่งดาวทุกดวง (ยกเว้นอาทิตย์) เหลือแค่ "ราศี" (0-11) เพราะออกแบบมา
   สำหรับระบบ 12-channel เท่านั้น ที่นี่ดึงค่าก่อนปัดออกมาด้วย จึงได้องศาละเอียดของดาวทุกดวง —
   ตรวจสอบแล้ว (4 ก.ย. 2569) ว่าตรงกับตาราง §12 ของ zodiac-system-check-natal-vs-tape.md
   คลาดไม่เกิน 1 ลิปดา (ยกเว้นจันทร์คลาด ~10 ลิปดา ไม่กระทบราศี)
2. ลัคนา (ascendant) ต้นฉบับก็ปัดเหลือราศีเหมือนกัน ที่นี่พอร์ตแบบเก็บองศาละเอียด (อิงจาก
   asc3.js ที่ทีมโปรเจกต์นี้เขียนขยายไว้ก่อนหน้า) และเปิดให้กำหนด "เวลาอาทิตย์ขึ้นที่สมมุติ"
   ได้อิสระ แทนที่จะผูกตายตัวกับตาราง PROVINCE_TIME_OFFSETS ของต้นฉบับ — เพราะโปรเจกต์นี้
   verify แล้วว่าโหรไทยที่เป็นต้นทางของดวงอ้างอิงใช้อาทิตย์ขึ้น 06:00 คงที่ (ไม่ใช่อาทิตย์ขึ้นจริง
   ต่อจังหวัด) ดู zodiac-system-check-natal-vs-tape.md §6, §8, §13

ใช้ JS-style modulo/round (js_mod/js_round) ตลอดทั้งไฟล์ แทน % และ round() ปกติของ Python
เพราะ Python round() ปัดเลขคู่ (banker's rounding) และ % ของ Python คืนค่าไม่ติดลบเสมอเมื่อตัวหาร
เป็นบวก ต่างจาก JS ทั้งสองจุด — ถ้าใช้เฉย ๆ อาจเพี้ยนสำหรับปีเกิดที่ทำให้ค่ากลางบางตัวติดลบ
"""
from __future__ import annotations

import math
from dataclasses import dataclass

RASI_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์", "ตุลย์",
           "พิจิก", "ธนู", "มังกร", "กุมภ์", "มีน"]

QUADRANT_ADJUST_TABLE = {0: 0, 1: 244, 2: 427, 3: 488}

SIGN_DURATIONS_MINUTES = [120.0, 96.0, 72.0, 120.0, 144.0, 168.0, 168.0,
                           144.0, 120.0, 72.0, 96.0, 120.0]

# นาทีชดเชยเวลาอาทิตย์ขึ้นจริงแต่ละจังหวัด (จาก kongesque/thai-astrology)
# ใช้เฉพาะเมื่อเลือก sunrise_mode="province" — ค่าเริ่มต้นของปลั๊กอินนี้คือ "fixed" (06:00 คงที่)
PROVINCE_TIME_OFFSETS = {
    "กระบี่": 24, "กรุงเทพมหานคร": 18, "กาญจนบุรี": 22, "กาฬสินธุ์": 6,
    "กำแพงเพชร": 22, "ขอนแก่น": 9, "จันทบุรี": 12, "ฉะเชิงเทรา": 16,
    "ชลบุรี": 16, "ชัยนาท": 19, "ชัยภูมิ": 12, "ชุมพร": 23, "เชียงราย": 21,
    "เชียงใหม่": 24, "ตรัง": 22, "ตราด": 10, "ตาก": 23, "นครนายก": 15,
    "นครปฐม": 20, "นครพนม": 1, "นครราชสีมา": 12, "นครศรีธรรมราช": 20,
    "นครสวรรค์": 20, "นนทบุรี": 18, "นราธิวาส": 13, "น่าน": 17,
    "บึงกาฬ": 5, "บุรีรัมย์": 8, "ปทุมธานี": 18, "ประจวบคีรีขันธ์": 21,
    "ปราจีนบุรี": 15, "ปัตตานี": 15, "พระนครศรีอยุธยา": 18, "พะเยา": 20,
    "พังงา": 26, "พัทลุง": 20, "พิจิตร": 19, "พิษณุโลก": 19, "เพชรบุรี": 20,
    "เพชรบูรณ์": 15, "แพร่": 19, "ภูเก็ต": 27, "มหาสารคาม": 7,
    "มุกดาหาร": 1, "แม่ฮ่องสอน": 28, "ยโสธร": 3, "ยะลา": 15,
    "ร้อยเอ็ด": 5, "ระนอง": 26, "ระยอง": 15, "ราชบุรี": 21, "ลพบุรี": 17,
    "ลำปาง": 22, "ลำพูน": 24, "เลย": 13, "ศรีสะเกษ": 3, "สกลนคร": 3,
    "สงขลา": 18, "สตูล": 20, "สมุทรปราการ": 18, "สมุทรสงคราม": 20,
    "สมุทรสาคร": 19, "สระแก้ว": 12, "สระบุรี": 16, "สิงห์บุรี": 18,
    "สุโขทัย": 21, "สุพรรณบุรี": 20, "สุราษฎร์ธานี": 23, "สุรินทร์": 6,
    "หนองคาย": 9, "หนองบัวลำภู": 10, "อ่างทอง": 18, "อำนาจเจริญ": 1,
    "อุดรธานี": 9, "อุตรดิตถ์": 20, "อุทัยธานี": 20, "อุบลราชธานี": 1,
}

# เจ้าเรือนของราศี (ดัชนี 0-11 ตามลำดับ RASI_TH) ใช้คำนวณตนุเศษ
_MAP_PLANETS = {0: 3, 1: 6, 2: 4, 3: 2, 4: 1, 5: 4, 6: 6, 7: 3, 8: 5, 9: 7, 10: 8, 11: 5}
_SIGN_PLANET_KEY = {1: "sun", 2: "moon", 3: "mars", 4: "mercury", 5: "jupiter",
                     6: "venus", 7: "saturn", 8: "rahu", 9: "ketu", 0: "uranus"}


def js_mod(a: float, b: float) -> float:
    """เลียนแบบ % ของ JavaScript (truncated division เครื่องหมายตามตัวตั้ง) ไม่ใช่ % ของ Python"""
    return a - b * math.trunc(a / b)


def js_round(x: float) -> int:
    """เลียนแบบ Math.round ของ JavaScript (ปัดขึ้นเสมอเมื่อเศษ .5 พอดี) ไม่ใช่ round() ของ Python"""
    return math.floor(x + 0.5)


def wrap21600(value: float) -> float:
    m = js_mod(value, 21600)
    return m if m >= 0 else m + 21600


@dataclass
class _BaseValues:
    relative_julian_day: float
    time_of_day_hours: float
    solar_cycle_base_minutes: float
    solar_longitude_corrected: float
    solar_longitude_mean: float


def _base_values(month_th: int, year_be: int, day: int, hour: float, minute: float) -> _BaseValues:
    year_ad = year_be - 543
    julian_year = year_ad if month_th > 2 else year_ad - 1
    julian_month = month_th + 1 if month_th > 2 else month_th + 13
    century_component = math.floor(julian_year * 0.01)
    julian_day_base = (math.floor(julian_year * 365.25) + math.floor(julian_month * 30.6)
                        + day + 1720997 - century_component + math.floor(century_component * 0.25))
    if hour < 12:
        julian_day_integer = julian_day_base - 1
        fractional_day_base = hour / 24 - 0.5 + 1.5
    else:
        julian_day_integer = julian_day_base
        fractional_day_base = hour / 24 - 0.5
    fractional_day_offset = (hour / 60 + minute) / 60 / 60 / 24
    fractional_julian_day = fractional_day_base + fractional_day_offset
    julian_day = julian_day_integer + fractional_julian_day
    relative_julian_day = js_round(julian_day - 1954167.5)
    time_of_day_hours = hour + minute / 60
    relative_year_from_1181 = year_be - 1181

    solar_calendar_ceiling = math.ceil((292207 * relative_year_from_1181 + 373) / 800)
    solar_equation_correction = (relative_year_from_1181 * 0.25875
                                  + math.trunc(relative_year_from_1181 / 100 + 0.38)
                                  - math.trunc(relative_year_from_1181 / 4 + 0.5)
                                  - math.trunc(relative_year_from_1181 / 400 + 0.595)
                                  - 5.53375)
    solar_correction_days = math.trunc(solar_equation_correction)
    solar_correction_hours = math.trunc((solar_equation_correction - solar_correction_days) * 24)
    solar_correction_minutes = math.trunc(((solar_equation_correction - solar_correction_days) * 24
                                            - solar_correction_hours) * 60)
    current_time_minutes = hour * 60 + minute / 60
    solar_correction_minutes_total = solar_correction_hours * 60 + solar_correction_minutes / 60
    solar_correction_comparison = 1 if current_time_minutes > solar_correction_minutes_total else 2

    if (relative_julian_day < solar_calendar_ceiling
            or (relative_julian_day == solar_calendar_ceiling and solar_correction_comparison == 2)):
        solar_cycle_year = relative_year_from_1181 - 1
    else:
        solar_cycle_year = relative_year_from_1181

    solar_cycle_position = js_mod(
        (relative_julian_day - 1) * 800 + math.trunc((time_of_day_hours * 800) / 24) - 373, 292207)
    solar_cycle_remainder = js_mod(solar_cycle_position, 24350)
    solar_cycle_turns = math.floor(solar_cycle_position / 24350)
    solar_cycle_degrees = math.floor(solar_cycle_remainder / 811)
    solar_cycle_degree_remainder = js_mod(solar_cycle_remainder, 811)
    solar_cycle_minutes = math.floor(solar_cycle_degree_remainder / 14) - 3
    solar_mean_longitude_raw = solar_cycle_turns * 1800 + solar_cycle_degrees * 60 + solar_cycle_minutes
    solar_longitude_mean = wrap21600(solar_mean_longitude_raw)
    solar_longitude_corrected = wrap21600(solar_longitude_mean - 23)
    solar_cycle_base_offset = (solar_cycle_year - 610) if solar_cycle_position >= 364 else (solar_cycle_year - 611)
    solar_cycle_base_minutes = solar_cycle_base_offset * 21600 + solar_longitude_corrected

    return _BaseValues(relative_julian_day, time_of_day_hours, solar_cycle_base_minutes,
                        solar_longitude_corrected, solar_longitude_mean)


def _describe_quadrant(value: float):
    normalized = wrap21600(value)
    quadrant_index = math.floor(normalized / 5400) + 1
    direction = -1 if quadrant_index in (1, 2) else 1
    if quadrant_index == 1:
        arc = normalized
    elif quadrant_index == 2:
        arc = 10800 - normalized
    elif quadrant_index == 3:
        arc = normalized - 10800
    else:
        arc = 21600 - normalized
    return quadrant_index, arc, direction


def _lookup_quadrant_adjustment_fixed(arc_minutes: float) -> int:
    base_index = math.floor(arc_minutes / 1800)
    lower = QUADRANT_ADJUST_TABLE[base_index % 4]
    upper = QUADRANT_ADJUST_TABLE[(base_index + 1) % 4]
    factor = arc_minutes / 1800 - base_index
    interpolated = factor * (upper - lower) + lower
    return js_round(interpolated * 60)


def _secondary_adjustment_parameters(value: float):
    normalized = wrap21600(value)
    quadrant_index = math.floor(normalized / 5400) + 1
    if quadrant_index == 1:
        secondary_arc = 5400 - normalized
    elif quadrant_index == 2:
        secondary_arc = normalized - 5400
    elif quadrant_index == 3:
        secondary_arc = 16200 - normalized
    else:
        secondary_arc = normalized - 16200
    base_index = math.floor(secondary_arc / 1800)
    lower = QUADRANT_ADJUST_TABLE[base_index % 4]
    upper = QUADRANT_ADJUST_TABLE[(base_index + 1) % 4]
    factor = secondary_arc / 1800 - base_index
    interpolated_adjustment = js_round(factor * (upper - lower) + lower + 0.5)
    half_adjustment = math.floor(interpolated_adjustment / 2)
    secondary_direction = 1 if quadrant_index in (1, 4) else -1
    return half_adjustment, secondary_direction, interpolated_adjustment


def _apply_planetary_adjustments(initial_pos: float, base_calc_val: float,
                                  primary_offset_baseline: float, primary_denominator_base: float,
                                  secondary_scale_factor: float) -> float:
    primary_offset = initial_pos - primary_offset_baseline
    _, primary_quadrant_arc, primary_direction = _describe_quadrant(primary_offset)
    primary_table_adjustment = _lookup_quadrant_adjustment_fixed(primary_quadrant_arc)
    primary_half_adjustment, primary_secondary_direction, _ = _secondary_adjustment_parameters(wrap21600(primary_offset))
    primary_denominator = primary_denominator_base + primary_half_adjustment * primary_secondary_direction
    primary_adjustment = js_round((primary_table_adjustment * 60) / primary_denominator) if primary_denominator != 0 else 0
    position_after_primary = initial_pos + primary_adjustment * primary_direction

    secondary_offset = wrap21600(position_after_primary) - base_calc_val
    _, secondary_quadrant_arc, secondary_direction = _describe_quadrant(secondary_offset)
    secondary_table_adjustment = _lookup_quadrant_adjustment_fixed(secondary_quadrant_arc)
    rounded_secondary_adjustment = js_round(js_round(secondary_table_adjustment / 60) / 3)
    scaled_primary_denominator = js_round(primary_denominator * secondary_scale_factor)
    secondary_numerator_base = rounded_secondary_adjustment + scaled_primary_denominator
    _, interpolation_direction, secondary_interpolated_adjustment = _secondary_adjustment_parameters(wrap21600(secondary_offset))
    secondary_denominator = secondary_numerator_base + secondary_interpolated_adjustment * interpolation_direction
    secondary_adjustment = js_round((secondary_table_adjustment * 60) / secondary_denominator) if secondary_denominator != 0 else 0
    final_pos = wrap21600(position_after_primary) + secondary_adjustment * secondary_direction
    return wrap21600(final_pos)


def _sun_precise_arcmin(month_th: int, year_be: int, day: int, hour: float, minute: float) -> float:
    g_vals_sun = {0: 0.0, 1: 35.0, 2: 67.0, 3: 94.0, 4: 116.0, 5: 129.0, 6: 134.0}
    bv = _base_values(month_th, year_be, day, hour, minute)
    mean_anomaly = wrap21600(bv.solar_longitude_mean - 4800)
    quadrant_index = math.floor(math.trunc(mean_anomaly / 5400)) + 1
    direction = -1 if quadrant_index in (1, 2) else 1
    if quadrant_index == 1:
        arc = mean_anomaly
    elif quadrant_index == 2:
        arc = 10800 - mean_anomaly
    elif quadrant_index == 3:
        arc = mean_anomaly - 10800
    else:
        arc = 21600 - mean_anomaly
    table_index_floor = math.floor(math.trunc(arc / 900))
    table_index_ceil = table_index_floor + 1
    table_value_floor = g_vals_sun.get(table_index_floor, g_vals_sun[6])
    table_value_ceil = g_vals_sun.get(table_index_ceil, g_vals_sun[6])
    factor = arc / 900 - table_index_floor
    adjustment = math.floor(math.trunc(factor * (table_value_ceil - table_value_floor) + table_value_floor))
    return wrap21600(bv.solar_longitude_mean + adjustment * direction)


def _moon_arcmin(month_th: int, year_be: int, day: int, hour: float, minute: float) -> float:
    g_vals_moon = {0: 0.0, 1: 77.0, 2: 148.0, 3: 209.0, 4: 256.0, 5: 286.0, 6: 296.0}
    bv = _base_values(month_th, year_be, day, hour, minute)
    lunar_mean_cycle = js_mod((bv.relative_julian_day - 1) * 703 + 650
                               + math.trunc((bv.time_of_day_hours * 703) / 24), 20760)
    mean_cycle_quotient = math.floor(lunar_mean_cycle / 692)
    mean_cycle_remainder = js_mod(lunar_mean_cycle, 692)
    mean_longitude_estimate = (mean_cycle_quotient * 720 + math.trunc(1.04 * mean_cycle_remainder)
                                - 40 + bv.solar_longitude_mean)
    mean_longitude = wrap21600(mean_longitude_estimate)
    anomaly_cycle = js_mod(bv.relative_julian_day - 1 - 621, 3232)
    anomaly_longitude = math.trunc(((anomaly_cycle + bv.time_of_day_hours / 24) / 3232) * 21600) + 2
    anomaly_longitude_wrapped = wrap21600(anomaly_longitude)
    longitude_difference = wrap21600(mean_longitude - anomaly_longitude_wrapped)
    quadrant_index = math.floor(math.trunc(longitude_difference / 5400)) + 1
    direction = -1 if quadrant_index in (1, 2) else 1
    if quadrant_index == 1:
        arc = longitude_difference
    elif quadrant_index == 2:
        arc = 10800 - longitude_difference
    elif quadrant_index == 3:
        arc = longitude_difference - 10800
    else:
        arc = 21600 - longitude_difference
    table_index_floor = math.floor(math.trunc(arc / 900))
    table_index_ceil = table_index_floor + 1
    table_value_floor = g_vals_moon.get(table_index_floor, g_vals_moon[6])
    table_value_ceil = g_vals_moon.get(table_index_ceil, g_vals_moon[6])
    factor = arc / 900 - table_index_floor
    adjustment = math.floor(math.trunc(factor * (table_value_ceil - table_value_floor) + table_value_floor))
    return wrap21600(mean_longitude + adjustment * direction)


def _uranus_arcmin(bv: _BaseValues) -> float:
    primary = math.floor(math.trunc(bv.solar_cycle_base_minutes / 84))
    secondary = math.floor(bv.solar_cycle_base_minutes / 7224)
    mean_longitude = js_mod(primary + secondary + 16277, 21600)
    return _apply_planetary_adjustments(mean_longitude, bv.solar_longitude_corrected, 7440, 38640, 3 / 7)


def _ketu_arcmin(bv: _BaseValues) -> float:
    lunar_node_cycle_offset = js_mod(bv.relative_julian_day - 1 - 344, 679)
    normalized_cycle_position = math.trunc(((lunar_node_cycle_offset + bv.time_of_day_hours / 24) * 21600) / 679)
    position_within_cycle = js_mod(normalized_cycle_position, 21600)
    return wrap21600(21600 - position_within_cycle)


def _rahu_arcmin(bv: _BaseValues) -> float:
    primary = math.floor(bv.solar_cycle_base_minutes / 20)
    secondary = math.floor(bv.solar_cycle_base_minutes / 265)
    wrapped = js_mod(primary + secondary, 21600)
    return wrap21600(15150 - wrapped)


def _saturn_arcmin(bv: _BaseValues) -> float:
    primary = math.floor(math.trunc(bv.solar_cycle_base_minutes / 30))
    secondary = math.floor((bv.solar_cycle_base_minutes * 6) / 10000)
    mean_longitude = js_mod(primary + secondary + 11944, 21600)
    return _apply_planetary_adjustments(mean_longitude, bv.solar_longitude_corrected, 14820, 3780, 7 / 6)


def _venus_arcmin(bv: _BaseValues) -> float:
    primary_cycle = math.floor(math.trunc((bv.solar_cycle_base_minutes * 5) / 3))
    secondary_cycle = math.floor((bv.solar_cycle_base_minutes * 10) / 243)
    venus_mean_longitude = js_mod(primary_cycle - secondary_cycle + 10944, 21600)
    primary_offset = bv.solar_longitude_corrected - 4800
    _, primary_quadrant_arc, primary_direction = _describe_quadrant(primary_offset)
    primary_table_adjustment = _lookup_quadrant_adjustment_fixed(primary_quadrant_arc)
    primary_half_adjustment, primary_secondary_direction, _ = _secondary_adjustment_parameters(wrap21600(primary_offset))
    primary_denominator = 19200 + primary_half_adjustment * primary_secondary_direction
    primary_adjustment = js_round((primary_table_adjustment * 60) / primary_denominator) if primary_denominator != 0 else 0
    position_after_primary = bv.solar_longitude_corrected + primary_adjustment * primary_direction
    secondary_offset = wrap21600(position_after_primary) - venus_mean_longitude
    _, secondary_quadrant_arc, secondary_direction = _describe_quadrant(secondary_offset)
    secondary_table_adjustment = _lookup_quadrant_adjustment_fixed(secondary_quadrant_arc)
    rounded_secondary_adjustment = js_round(js_round(secondary_table_adjustment / 60) / 3)
    fixed_venus_adjustment = 60 * 11
    secondary_numerator_base = rounded_secondary_adjustment + fixed_venus_adjustment
    _, interpolation_direction, secondary_interpolated_adjustment = _secondary_adjustment_parameters(wrap21600(secondary_offset))
    secondary_denominator = secondary_numerator_base + secondary_interpolated_adjustment * interpolation_direction
    secondary_adjustment = js_round((secondary_table_adjustment * 60) / secondary_denominator) if secondary_denominator != 0 else 0
    return wrap21600(wrap21600(position_after_primary) + secondary_adjustment * secondary_direction)


def _mercury_arcmin(bv: _BaseValues) -> float:
    primary_cycle = math.floor(math.trunc((bv.solar_cycle_base_minutes * 7) / 46))
    secondary_cycle = math.floor(bv.solar_cycle_base_minutes * 4)
    mercury_mean_longitude = js_mod(primary_cycle + secondary_cycle + 10642, 21600)
    primary_offset = bv.solar_longitude_corrected - 13200
    _, primary_quadrant_arc, primary_direction = _describe_quadrant(primary_offset)
    primary_table_adjustment = _lookup_quadrant_adjustment_fixed(primary_quadrant_arc)
    primary_half_adjustment, primary_secondary_direction, _ = _secondary_adjustment_parameters(wrap21600(primary_offset))
    primary_denominator = 6000 + primary_half_adjustment * primary_secondary_direction
    primary_adjustment = js_round((primary_table_adjustment * 60) / primary_denominator) if primary_denominator != 0 else 0
    position_after_primary = bv.solar_longitude_corrected + primary_adjustment * primary_direction
    secondary_offset = wrap21600(position_after_primary) - mercury_mean_longitude
    _, secondary_quadrant_arc, secondary_direction = _describe_quadrant(secondary_offset)
    secondary_table_adjustment = _lookup_quadrant_adjustment_fixed(secondary_quadrant_arc)
    rounded_secondary_adjustment = js_round(js_round(secondary_table_adjustment / 60) / 3)
    fixed_mercury_adjustment = 60 * 21
    secondary_numerator_base = rounded_secondary_adjustment + fixed_mercury_adjustment
    _, interpolation_direction, secondary_interpolated_adjustment = _secondary_adjustment_parameters(wrap21600(secondary_offset))
    secondary_denominator = secondary_numerator_base + secondary_interpolated_adjustment * interpolation_direction
    secondary_adjustment = js_round((secondary_table_adjustment * 60) / secondary_denominator) if secondary_denominator != 0 else 0
    return wrap21600(wrap21600(position_after_primary) + secondary_adjustment * secondary_direction)


def _mars_arcmin(bv: _BaseValues) -> float:
    primary = math.floor(math.trunc(bv.solar_cycle_base_minutes / 2))
    secondary = math.floor((bv.solar_cycle_base_minutes * 16) / 505)
    mean_longitude = js_mod(primary + secondary + 5420, 21600)
    return _apply_planetary_adjustments(mean_longitude, bv.solar_longitude_corrected, 7620, 2700, 4 / 15)


def _ascendant_arcmin(day: int, month_th: int, year_be: int, hour: float, minute: float,
                       sunrise_offset_minutes: float) -> float:
    """ลัคนาแบบละเอียด (พอร์ตจาก asc3.js) — sunrise_offset_minutes คือนาทีที่บวกจาก 06:00
    เป็น "เวลาอาทิตย์ขึ้นที่สมมุติ" (0 = อาทิตย์ขึ้น 06:00 คงที่ ตามที่โปรเจกต์นี้ยืนยันว่าตรงเทป)"""
    sun_arcmin = _sun_precise_arcmin(month_th, year_be, day, hour, minute)
    sun_sign_index = math.floor(math.trunc(sun_arcmin / 1800))
    sun_minutes_in_sign = js_mod(sun_arcmin, 1800)
    sun_degrees_within_sign = math.trunc(sun_minutes_in_sign / 60)
    sun_minutes_within_degree = math.trunc(js_mod(sun_minutes_in_sign, 60))

    local_time_minutes = hour * 60 + minute
    minutes_before_sun_sign = sum(SIGN_DURATIONS_MINUTES[:sun_sign_index])
    sun_progress_degrees = sun_degrees_within_sign + sun_minutes_within_degree / 60
    sun_sign_duration_minutes = SIGN_DURATIONS_MINUTES[sun_sign_index]
    sun_traversal_minutes = (sun_sign_duration_minutes * (sun_progress_degrees / 30)
                              if sun_sign_duration_minutes > 0 else 0)
    sun_total_progression_minutes = minutes_before_sun_sign + sun_traversal_minutes

    sunrise_time_minutes = 360 + sunrise_offset_minutes
    elapsed = js_mod(local_time_minutes - sunrise_time_minutes, 1440)
    if elapsed < 0:
        elapsed += 1440
    ascendant_minutes_of_day = js_mod(sun_total_progression_minutes + elapsed, 1440)
    if ascendant_minutes_of_day < 0:
        ascendant_minutes_of_day += 1440

    cumulative = 0.0
    ascendant_sign_index = 0
    degrees_within_ascendant_sign = 0.0
    for i, duration in enumerate(SIGN_DURATIONS_MINUTES):
        start, end = cumulative, cumulative + duration
        wraps = start >= end
        within = (ascendant_minutes_of_day >= start or ascendant_minutes_of_day < end) if wraps \
            else (start <= ascendant_minutes_of_day < end)
        if within:
            ascendant_sign_index = i
            minutes_into = js_mod(ascendant_minutes_of_day - start, 1440)
            if minutes_into < 0:
                minutes_into += 1440
            degrees_within_ascendant_sign = minutes_into * 30 / duration
            break
        cumulative = end % 1440

    return (ascendant_sign_index * 30 + degrees_within_ascendant_sign) * 60


def _arcmin_to_longitude(arcmin: float) -> float:
    """แปลงหน่วยลิปดา (0-21600) เป็นองศาสัมบูรณ์ (0-360)"""
    return arcmin / 60.0


def calculate_positions(day: int, month_th: int, year_be: int, hour: float, minute: float,
                         sunrise_offset_minutes: float = 0.0) -> dict:
    """คืนตำแหน่งดาวสุริยยาตร์แบบละเอียด (longitude 0-360 สำหรับทุกดวง) + ลัคนา + ตนุเศษ

    day, month_th (1=เมษายน... ตามปฏิทินจันทรคติไทย ไม่ใช่เดือนสากล — ใช้ค่าเดียวกับที่
    kongesque/thai-astrology รับ คือ "เดือนที่" ตามระบบสุริยยาตร์ ปกติ = เดือนสากล 1-12 ตรง ๆ
    สำหรับวันที่หลัง พ.ศ. ปัจจุบัน), year_be = พ.ศ., hour/minute = เวลาเกิด (24 ชม.)
    sunrise_offset_minutes = นาทีชดเชยจาก 06:00 (ค่าเริ่มต้น 0 = อาทิตย์ขึ้น 06:00 คงที่)
    """
    bv = _base_values(month_th, year_be, day, hour, minute)

    sun_arcmin = _sun_precise_arcmin(month_th, year_be, day, hour, minute)
    positions_arcmin = {
        "sun": sun_arcmin,
        "moon": _moon_arcmin(month_th, year_be, day, hour, minute),
        "mars": _mars_arcmin(bv),
        "mercury": _mercury_arcmin(bv),
        "jupiter": _apply_planetary_adjustments(
            js_mod(math.floor(math.trunc(bv.solar_cycle_base_minutes / 12))
                   + math.floor(bv.solar_cycle_base_minutes / 1032) + 14297, 21600),
            bv.solar_longitude_corrected, 10320, 5520, 3 / 7),
        "venus": _venus_arcmin(bv),
        "saturn": _saturn_arcmin(bv),
        "rahu": _rahu_arcmin(bv),
        "ketu": _ketu_arcmin(bv),
        "uranus": _uranus_arcmin(bv),
    }
    ascendant_arcmin = _ascendant_arcmin(day, month_th, year_be, hour, minute, sunrise_offset_minutes)

    longitudes = {k: _arcmin_to_longitude(v) for k, v in positions_arcmin.items()}
    longitudes["ascendant"] = _arcmin_to_longitude(ascendant_arcmin)

    # ตนุเศษ (tanuseth) — ใช้ราศี (sign index 0-11) ไม่ใช่องศา ตามอัลกอริทึมต้นฉบับ
    sign_index = {k: int(v // 30) for k, v in longitudes.items()}
    tanuseth = _tanuseth(sign_index)

    return {
        "longitudes": longitudes,          # องศาสัมบูรณ์ 0-360 ของทุกดวง + ascendant
        "sign_index": sign_index,
        "tanuseth": tanuseth,
        "sunrise_offset_minutes": sunrise_offset_minutes,
    }


def _tanuseth(sign_index: dict) -> int:
    try:
        asc_sign = sign_index["ascendant"]
        lord1_idx = _MAP_PLANETS[asc_sign]
        lord1_key = _SIGN_PLANET_KEY[lord1_idx]
        first_lord_sign = sign_index[lord1_key]
        lord2_idx = _MAP_PLANETS[first_lord_sign]
        lord2_key = _SIGN_PLANET_KEY[lord2_idx]
        second_lord_sign = sign_index[lord2_key]
        asc_distance = js_mod(first_lord_sign - asc_sign, 12) + 1
        second_step_distance = js_mod(second_lord_sign - first_lord_sign, 12) + 1
        result = js_mod(asc_distance * second_step_distance, 7)
        return int(result) if result else 7
    except Exception:
        return -1
