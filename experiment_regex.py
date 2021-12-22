from edtf.parser import parse_edtf

year = parse_edtf('1986')
print(year)
year_month = parse_edtf('1986-01')
print(year_month)
year_month_day = parse_edtf('1986-01-07')
print(year_month_day)
date_and_time = parse_edtf('2004-01-01T10:10:10+05:00')
print(date_and_time)
day_and_month_unspecified = parse_edtf('1999-XX-XX')
print(day_and_month_unspecified)