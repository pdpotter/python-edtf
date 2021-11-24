import regex

from pyparsing import Literal as L, ParseException, Optional, OneOrMore, \
    ZeroOrMore, oneOf, Regex, Combine, Word, NotAny, nums

from edtf.parser.parser_classes import Date, DateAndTime, Interval, Unspecified, \
    UncertainOrApproximate, Level1Interval, LongYear, Season, \
    PartialUncertainOrApproximate, UA, PartialUnspecified, OneOfASet, \
    Consecutives, EarlierConsecutives, LaterConsecutives, MultipleDates, \
    MaskedPrecision, Level2Interval, ExponentialYear

from edtf.parser.edtf_exceptions import EDTFParseException


# (* ************************** Level 0 *************************** *)

RE = {}

def add_re(name: str, reg_ex: str):
    RE[name] = [
        regex.compile(fr'^{reg_ex}$'),
        regex.compile(reg_ex),
]

one_thru_12 = r'0[123456789]|1[012]'
one_thru_13 = r'0[123456789]|1[0123]'
one_thru_23 = r'0[123456789]|1[0123456789]|2[0123]'
zero_thru_23 = r'[01][0123456789]|2[0123]'
one_thru_29 = r'0[123456789]|[12][0123456789]'
one_thru_30 = r'0[123456789]|[12][0123456789]|30'
one_thru_31 = r'0[123456789]|[12][0123456789]|3[01]'
one_thru_59 = r'0[123456789]|[12345][0123456789]'
zero_thru_59 = r'[012345][0123456789]'

positive_digit = r'[123456789]'
digit = r'[0123456789]'

second = zero_thru_59
minute = zero_thru_59
hour = zero_thru_23
day = fr'(?P<day>{one_thru_31})'

month = fr'(?P<month>{one_thru_12})'
month_day = (
    fr'(?:(?P<month>0[13578]|1[02])-(?P<day>{one_thru_31}))'
    fr'|(?:(?P<month>0[469]|11)-(?P<day>{one_thru_30}))'
    fr'|(?:(?P<month>02)-(?P<day>{one_thru_29}))'
)

positive_year = r'[0123456789]{4}'
negative_year = fr'(?!-0000)-{positive_year}'

year = fr'(?P<year>{positive_year}|{negative_year})'
year_month = fr'{year}-{month}'
year_month_day = fr'{year}-(?:{month_day})'

date = fr'(?P<date>{year}|{year_month}|{year_month_day})'

# zone_offset_hour = one_thru_13
# zone_offset = fr'Z|[+-]'




add_re('year_month_day', year_month_day)
add_re('year_month', year_month)
add_re('year', year)



oneThru12 = oneOf(['%.2d' % i for i in range(1, 13)])
oneThru13 = oneOf(['%.2d' % i for i in range(1, 14)])
oneThru23 = oneOf(['%.2d' % i for i in range(1, 24)])
zeroThru23 = oneOf(['%.2d' % i for i in range(0, 23)])
oneThru29 = oneOf(['%.2d' % i for i in range(1, 30)])
oneThru30 = oneOf(['%.2d' % i for i in range(1, 31)])
oneThru31 = oneOf(['%.2d' % i for i in range(1, 32)])
oneThru59 = oneOf(['%.2d' % i for i in range(1, 60)])
zeroThru59 = oneOf(['%.2d' % i for i in range(0, 60)])

positiveDigit = Word(nums, exact=1, excludeChars='0')
digit = Word(nums, exact=1)

second = zeroThru59
minute = zeroThru59
hour = zeroThru23
day = oneThru31("day")

month = oneThru12("month")
monthDay = (
    (oneOf("01 03 05 07 08 10 12")("month") + "-" + oneThru31("day")) ^
    (oneOf("04 06 09 11")("month") + "-" + oneThru30("day")) ^
    (L("02")("month") + "-" + oneThru29("day"))
)

# 4 digits, 0 to 9
positiveYear = Word(nums, exact=4)

# Negative version of positive year, but "-0000" is illegal
negativeYear = NotAny(L("-0000")) + ("-" + positiveYear)

year = Combine(positiveYear ^ negativeYear)("year")

yearMonth = year + "-" + month
yearMonthDay = year + "-" + monthDay  # o hai iso date

date = Combine(year ^ yearMonth ^ yearMonthDay)("date")
Date.set_parser(date)

zoneOffsetHour = oneThru13
zoneOffset = L("Z") ^ (
    Regex("[+-]") + (
        zoneOffsetHour + Optional(":" + minute) ^
        L("14:00") ^
        ("00:" + oneThru59)
    )
)

baseTime = Combine(hour + ":" + minute + ":" + second ^ "24:00:00")

time = Combine(baseTime + Optional(zoneOffset))("time")

dateAndTime = date + "T" + time
DateAndTime.set_parser(dateAndTime)

l0Interval = date("lower") + "/" + date("upper")
Interval.set_parser(l0Interval)

level0Expression = date ^ dateAndTime ^ l0Interval


# (* ************************** Level 1 *************************** *)

# (* ** Auxiliary Assignments for Level 1 ** *)
UASymbol = Combine(oneOf("? ~ ?~"))
UA.set_parser(UASymbol)

seasonNumber = oneOf("21 22 23 24")

# (* *** Season (unqualified) *** *)
season = year + "-" + seasonNumber("season")
Season.set_parser(season)

dateOrSeason = date("") ^ season

# (* *** Long Year - Simple Form *** *)

longYearSimple = "y" + Combine(
    Optional("-") + positiveDigit + digit + digit + digit + OneOrMore(digit)
)("year")
LongYear.set_parser(longYearSimple)

# (* *** L1Interval *** *)
uaDateOrSeason = dateOrSeason + Optional(UASymbol)
l1Start = uaDateOrSeason ^ "unknown"


# bit of a kludge here to get the all the relevant tokens into the parse action
# cleanly otherwise the parameter names are overlapped.
def f(toks):
    try:
        return {'date': toks[0], 'ua': toks[1]}
    except IndexError:
        return {'date': toks[0], 'ua': None}


l1Start.addParseAction(f)
l1End = uaDateOrSeason ^ "unknown" ^ "open"
l1End.addParseAction(f)

level1Interval = l1Start("lower") + "/" + l1End("upper")
Level1Interval.set_parser(level1Interval)

# (* *** unspecified *** *)
yearWithOneOrTwoUnspecifedDigits = Combine(
    digit + digit + (digit ^ 'u') + 'u'
)("year")
monthUnspecified = year + "-" + L("uu")("month")
dayUnspecified = yearMonth + "-" + L("uu")("day")
dayAndMonthUnspecified = year + "-" + L("uu")("month") + "-" + L("uu")("day")

unspecified = yearWithOneOrTwoUnspecifedDigits \
    ^ monthUnspecified \
    ^ dayUnspecified \
    ^ dayAndMonthUnspecified
Unspecified.set_parser(unspecified)

# (* *** uncertainOrApproxDate *** *)

uncertainOrApproxDate = date('date') + UASymbol("ua")
UncertainOrApproximate.set_parser(uncertainOrApproxDate)

level1Expression = uncertainOrApproxDate \
    ^ unspecified \
    ^ level1Interval \
    ^ longYearSimple \
    ^ season

# (* ************************** Level 2 *************************** *)

# (* ** Internal Unspecified** *)

digitOrU = Word(nums + 'u', exact=1)

# 2-digit day with at least one 'u' present
dayWithU = Combine(
    ("u" + digitOrU) ^
    (digitOrU + 'u')
)("day")

# 2-digit month with at least one 'u' present
monthWithU = Combine(
    oneOf("0u 1u") ^
    ("u" + digitOrU)
)("month")

# 4-digit year with at least one 'u' present
yearWithU = Combine(
    ('u' + digitOrU + digitOrU + digitOrU) ^
    (digitOrU + 'u' + digitOrU + digitOrU) ^
    (digitOrU + digitOrU + 'u' + digitOrU) ^
    (digitOrU + digitOrU + digitOrU + 'u')
)("year")

yearMonthWithU = (
    (Combine(year("") ^ yearWithU(""))("year") + "-" + monthWithU) ^
    (yearWithU + "-" + month)
)

monthDayWithU = (
    (Combine(month("") ^ monthWithU(""))("month") + "-" + dayWithU) ^
    (monthWithU + "-" + day)
)

yearMonthDayWithU = (
    (yearWithU + "-" + Combine(month("") ^ monthWithU(""))("month") + "-" + Combine(day("") ^ dayWithU(""))("day")) ^
    (year + "-" + monthWithU + "-" + Combine(day("") ^ dayWithU(""))("day")) ^
    (year + "-" + month + "-" + dayWithU)
)

partialUnspecified = yearWithU ^ yearMonthWithU ^ yearMonthDayWithU
PartialUnspecified.set_parser(partialUnspecified)

# (* ** Internal Uncertain or Approximate** *)

# this line is out of spec, but the given examples (e.g. '(2004)?-06-04~')
# appear to require it.
year_with_brackets = year ^ ("(" + year + ")")

# second clause below needed Optional() around the "year_ua" UASymbol, for dates
# like '(2011)-06-04~' to work.

IUABase = \
    (year_with_brackets + UASymbol("year_ua") + "-" + month + Optional("-(" + day + ")" + UASymbol("day_ua"))) \
    ^ (year_with_brackets + Optional(UASymbol)("year_ua") + "-" + monthDay + Optional(UASymbol)("month_day_ua")) \
    ^ (
        year_with_brackets + Optional(UASymbol)("year_ua") + "-(" + month + ")" + UASymbol("month_ua") +
        Optional("-(" + day + ")" + UASymbol("day_ua"))
    ) \
    ^ (
        year_with_brackets + Optional(UASymbol)("year_ua") + "-(" + month + ")" + UASymbol("month_ua") +
        Optional("-" + day)
    ) \
    ^ (yearMonth + UASymbol("year_month_ua") + "-(" + day + ")" + UASymbol("day_ua")) \
    ^ (yearMonth + UASymbol("year_month_ua") + "-" + day) \
    ^ (yearMonth + "-(" + day + ")" + UASymbol("day_ua")) \
    ^ (year + "-(" + monthDay + ")" + UASymbol("month_day_ua")) \
    ^ (season("ssn") + UASymbol("season_ua"))

partialUncertainOrApproximate = IUABase ^ ("(" + IUABase + ")" + UASymbol("all_ua"))
PartialUncertainOrApproximate.set_parser(partialUncertainOrApproximate)

dateWithInternalUncertainty = partialUncertainOrApproximate \
                              ^ partialUnspecified

qualifyingString = Regex(r'\S')  # any nonwhitespace char

# (* ** SeasonQualified ** *)
seasonQualifier = qualifyingString
seasonQualified = season + "^" + seasonQualifier

# (* ** Long Year - Scientific Form ** *)
positiveInteger = Combine(positiveDigit + ZeroOrMore(digit))
longYearScientific = "y" + Combine(Optional("-") + positiveInteger)("base") + "e" + \
    positiveInteger("exponent") + Optional("p" + positiveInteger("precision"))
ExponentialYear.set_parser(longYearScientific)

# (* ** level2Interval ** *)
level2Interval = (dateOrSeason("lower") + "/" + dateWithInternalUncertainty("upper")) \
                 ^ (dateWithInternalUncertainty("lower") + "/" + dateOrSeason("upper")) \
                 ^ (dateWithInternalUncertainty("lower") + "/" + dateWithInternalUncertainty("upper"))
Level2Interval.set_parser(level2Interval)

# (* ** Masked precision ** *)
maskedPrecision = Combine(digit + digit + ((digit + "x") ^ "xx"))("year")
MaskedPrecision.set_parser(maskedPrecision)

# (* ** Inclusive list and choice list** *)
consecutives = (yearMonthDay("lower") + ".." + yearMonthDay("upper")) \
    ^ (yearMonth("lower") + ".." + yearMonth("upper")) \
    ^ (year("lower") + ".." + year("upper"))
Consecutives.set_parser(consecutives)

listElement = date \
    ^ dateWithInternalUncertainty \
    ^ uncertainOrApproxDate \
    ^ unspecified \
    ^ consecutives

earlier = ".." + date("upper")
EarlierConsecutives.set_parser(earlier)
later = date("lower") + ".."
LaterConsecutives.set_parser(later)

listContent = (earlier + ZeroOrMore("," + listElement)) \
    ^ (Optional(earlier + ",") + ZeroOrMore(listElement + ",") + later) \
    ^ (listElement + OneOrMore("," + listElement)) \
    ^ consecutives

choiceList = "[" + listContent + "]"
OneOfASet.set_parser(choiceList)

inclusiveList = "{" + listContent + "}"
MultipleDates.set_parser(inclusiveList)

level2Expression = partialUncertainOrApproximate \
                   ^ partialUnspecified \
                   ^ choiceList \
                   ^ inclusiveList \
                   ^ maskedPrecision \
                   ^ level2Interval \
                   ^ longYearScientific \
                   ^ seasonQualified

# putting it all together
edtfParser = level0Expression("level0") ^ level1Expression("level1") ^ level2Expression("level2")


def parse_edtf(str, parseAll=True, fail_silently=False):
    if not str:
        raise EDTFParseException('You must supply some input text')
    str = str.strip()
    if parseAll:
        # return first match
        # date
        if m:= RE['year_month_day'][0].search(str):
            print(RE['year_month_day'][0])
            print(m)
            return Date(year=m.group('year'), month=m.group('month'), day=m.group('day'))
        if m:= RE['year_month'][0].search(str):
            return Date(year=m.group('year'), month=m.group('month'))
        if m:= RE['year'][0].search(str):
            return Date(year=m.group('year'))
    # else:
    #     # return longest match
    #     size_longest_match = 0
    #     match = None
    #     # date
    #     if m:= RE['year_month_day'][1].search(str):
    #         match = Date(year=m.group('year'), month=m.group('month'), day=m.group('day'))
    #     elif m:= RE['year_month'][1].search(str):
    #         match = Date(year=m.group('year'), month=m.group('month'))
    #     elif m:= RE['year'][1].search(str):
    #         match = Date(year=m.group('year'))

    #     if match is not None:
    #         return match

    if fail_silently:
        return None
    raise EDTFParseException('Invalid Extended Date/Time Format')


    try:
        if not str:
            raise ParseException("You must supply some input text")
        p = edtfParser.parseString(str.strip(), parseAll)
        if p:
            return p[0]
    except ParseException as e:
        if fail_silently:
            return None
        raise EDTFParseException(e)
