from edtf.parser import parse_edtf

year = parse_edtf('1986')
print(year)
year_month = parse_edtf('1986-01')
print(year_month)
year_month_day = parse_edtf('1986-01-07')
print(year_month_day)