import pe

from pyparsing import Literal as L, ParseException, Optional, OneOrMore, \
    ZeroOrMore, oneOf, Regex, Combine, Word, NotAny, nums

from edtf.parser.parser_classes import Date, DateAndTime, Interval, Unspecified, \
    UncertainOrApproximate, Level1Interval, LongYear, Season, \
    PartialUncertainOrApproximate, UA, PartialUnspecified, OneOfASet, \
    Consecutives, EarlierConsecutives, LaterConsecutives, MultipleDates, \
    MaskedPrecision, Level2Interval, ExponentialYear

from edtf.parser.edtf_exceptions import EDTFParseException

edtf_parser = pe.compile(
    r'''
    Start                 <- l_0_expression EOF

    l_0_expression        <- date

    date                  <- year_month_day / year_month / year

    year_month_day        <- year '-' month_day
    year_month            <- year '-' month:(~(month))
    year                  <- year:(~(positive_year / negative_year))

    positive_year         <- [0123456789][0123456789][0123456789][0123456789]
    negative_year         <- !'-0000' '-'positive_year

    month                 <- one_thru_12

    month_day             <- month_day_31 / month_day_30 / month_day_29
    month_day_31          <- month:(~('0'[13578] / '1'[02])) '-' day:(~(one_thru_31))
    month_day_30          <- month:(~('0'[469] / '11')) '-' day:(~(one_thru_31))
    month_day_29          <- month:(~('02')) '-' day:(~(one_thru_29))

    one_thru_31           <- '0'[123456789] / [12][0123456789] / '3'[01]
    one_thru_30           <- '0'[123456789] / [12][0123456789] / '30'
    one_thru_29           <- '0'[123456789] / [12][0123456789]
    one_thru_12           <- '0'[123456789] / '1'[012]

    EOF                   <- !.
    ''',
    actions={
        'date': pe.actions.Call(Date)
    },
    flags=pe.Flag.DEBUG
)

# def create_compiled_regex(input):
#     return regex.compile(fr'^{input}$')

# def suffix_named_groups(input, groups, suffix):
#     result = input
#     for g in groups:
#         result = result.replace(f'<{g}>', f'<{g}_{suffix}>')
#     return result

# # (* ************************** Level 0 *************************** *)

# one_thru_12 = r'(?:0[123456789]|1[012])'
# one_thru_13 = r'(?:0[123456789]|1[0123])'
# one_thru_23 = r'(?:0[123456789]|1[0123456789]|2[0123])'
# zero_thru_23 = r'(?:[01][0123456789]|2[0123])'
# one_thru_29 = r'(?:0[123456789]|[12][0123456789])'
# one_thru_30 = r'(?:0[123456789]|[12][0123456789]|30)'
# one_thru_31 = r'(?:0[123456789]|[12][0123456789]|3[01])'
# one_thru_59 = r'(?:0[123456789]|[12345][0123456789])'
# zero_thru_59 = r'[012345][0123456789]'

# second = zero_thru_59
# minute = zero_thru_59
# hour = zero_thru_23
# day = fr'(?P<day>{one_thru_31})'

# month = fr'(?P<month>{one_thru_12})'
# month_day = (
#     r'(?:'
#     fr'(?P<month>0[13578]|1[02])-(?P<day>{one_thru_31})'
#     fr'|(?P<month>0[469]|11)-(?P<day>{one_thru_30})'
#     fr'|(?P<month>02)-(?P<day>{one_thru_29})'
#     r')'
# )

# positive_year = r'[0123456789]{4}'
# negative_year = fr'(?!-0000)-{positive_year}'

# year = fr'(?P<year>{positive_year}|{negative_year})'
# year_month = fr'{year}-{month}'
# year_month_day = fr'{year}-{month_day}'

# date = fr'(?P<date>{year}|{year_month}|{year_month_day})'

# zone_offset_hour = one_thru_13
# zone_offset = (
#     r'Z'
#     fr'|[+-]{zone_offset_hour}(?::{minute})?'
#     r'|14:00'
#     fr'|00:{one_thru_59}'
# )

# base_time = fr'(?:{hour}:{minute}:{second}|24:00:00)'

# time = fr'(?P<time>{base_time}(?:{zone_offset})?)'

# date_and_time = fr'{date}T{time}'

# date_lower = suffix_named_groups(date, ['year', 'month', 'day'], 'lower')
# date_upper = suffix_named_groups(date, ['year', 'month', 'day'], 'upper')

# l_0_interval = (
#     fr'{date_lower}'
#     r'/'
#     fr'{date_upper}'
# )

# re_date = create_compiled_regex(date)
# re_date_and_time = create_compiled_regex(date_and_time)
# re_l_0_interval = create_compiled_regex(l_0_interval)

# # (* ************************** Level 1 *************************** *)

# # (* ** Auxiliary Assignments for Level 1 ** *)
# uncertain_or_approximate = r'(?P<ua>[?~%])'

# season_number = r'(?P<season>[2][1234])'

# # (* *** Season (unqualified) *** *)
# season = fr'(?:{year}-{season_number})'

# date_or_season = fr'{date}|{season}'

# # (* *** Long Year - Simple Form *** *)
# long_year_simple = fr'(?P<year>Y-?[123456789][0123456789]{{3}}[0123456789]+)'

# # (* *** L1Interval *** *)
# uncertain_or_approximate_date_or_season = fr'(?:{date_or_season}{uncertain_or_approximate}?)'

# uncertain_or_approximate_date_or_season_lower = suffix_named_groups(uncertain_or_approximate_date_or_season, ['year', 'month', 'day', 'ua'], 'lower')
# uncertain_or_approximate_date_or_season_upper = suffix_named_groups(uncertain_or_approximate_date_or_season, ['year', 'month', 'day', 'ua'], 'upper')
# l_1_interval = (
#     fr'(?:{uncertain_or_approximate_date_or_season_lower}|(?P<open_lower>[.][.]))?'
#     r'/'
#     fr'(?:{uncertain_or_approximate_date_or_season_upper}|(?P<open_upper>[.][.]))?'
# )

# # (* *** unspecified *** *)
# year_with_one_or_two_unspecified_digits = r'(?P<year>[0123456789]{2}[0123456789X]X)'
# month_unspecified = fr'(?:{year}-(?P<month>XX))'
# day_unspecified = fr'(?:{year_month}-(?P<day>XX))'
# # TODO: fix
# day_and_month_unspecified = fr'(?:{year}-(?P<month>XX)-(?P<day>XX))'

# unspecified = fr'{year_with_one_or_two_unspecified_digits}|{month_unspecified}|{day_unspecified}|{day_and_month_unspecified}'

# # (* *** uncertainOrApproxDate *** *)
# uncertain_or_approximate_date = fr'{date}{uncertain_or_approximate}'

# re_uncertain_or_approximate_date = create_compiled_regex(uncertain_or_approximate_date)
# re_unspecified = create_compiled_regex(unspecified)
# re_l_1_interval = create_compiled_regex(l_1_interval)
# re_long_year_simple = create_compiled_regex(long_year_simple)
# re_season = create_compiled_regex(season)






# oneThru12 = oneOf(['%.2d' % i for i in range(1, 13)])
# oneThru13 = oneOf(['%.2d' % i for i in range(1, 14)])
# oneThru23 = oneOf(['%.2d' % i for i in range(1, 24)])
# zeroThru23 = oneOf(['%.2d' % i for i in range(0, 23)])
# oneThru29 = oneOf(['%.2d' % i for i in range(1, 30)])
# oneThru30 = oneOf(['%.2d' % i for i in range(1, 31)])
# oneThru31 = oneOf(['%.2d' % i for i in range(1, 32)])
# oneThru59 = oneOf(['%.2d' % i for i in range(1, 60)])
# zeroThru59 = oneOf(['%.2d' % i for i in range(0, 60)])

# positiveDigit = Word(nums, exact=1, excludeChars='0')
# digit = Word(nums, exact=1)

# second = zeroThru59
# minute = zeroThru59
# hour = zeroThru23
# day = oneThru31("day")

# month = oneThru12("month")
# monthDay = (
#     (oneOf("01 03 05 07 08 10 12")("month") + "-" + oneThru31("day")) ^
#     (oneOf("04 06 09 11")("month") + "-" + oneThru30("day")) ^
#     (L("02")("month") + "-" + oneThru29("day"))
# )

# # 4 digits, 0 to 9
# positiveYear = Word(nums, exact=4)

# # Negative version of positive year, but "-0000" is illegal
# negativeYear = NotAny(L("-0000")) + ("-" + positiveYear)

# year = Combine(positiveYear ^ negativeYear)("year")

# yearMonth = year + "-" + month
# yearMonthDay = year + "-" + monthDay  # o hai iso date

# date = Combine(year ^ yearMonth ^ yearMonthDay)("date")
# Date.set_parser(date)

# zoneOffsetHour = oneThru13
# zoneOffset = L("Z") ^ (
#     Regex("[+-]") + (
#         zoneOffsetHour + Optional(":" + minute) ^
#         L("14:00") ^
#         ("00:" + oneThru59)
#     )
# )

# baseTime = Combine(hour + ":" + minute + ":" + second ^ "24:00:00")

# time = Combine(baseTime + Optional(zoneOffset))("time")

# dateAndTime = date + "T" + time
# DateAndTime.set_parser(dateAndTime)

# l0Interval = date("lower") + "/" + date("upper")
# Interval.set_parser(l0Interval)

# level0Expression = date ^ dateAndTime ^ l0Interval


# # (* ************************** Level 1 *************************** *)

# # (* ** Auxiliary Assignments for Level 1 ** *)
# UASymbol = Combine(oneOf("? ~ ?~"))
# UA.set_parser(UASymbol)

# seasonNumber = oneOf("21 22 23 24")

# # (* *** Season (unqualified) *** *)
# season = year + "-" + seasonNumber("season")
# Season.set_parser(season)

# dateOrSeason = date("") ^ season

# # (* *** Long Year - Simple Form *** *)

# longYearSimple = "y" + Combine(
#     Optional("-") + positiveDigit + digit + digit + digit + OneOrMore(digit)
# )("year")
# LongYear.set_parser(longYearSimple)

# # (* *** L1Interval *** *)
# uaDateOrSeason = dateOrSeason + Optional(UASymbol)
# l1Start = uaDateOrSeason ^ "unknown"


# # bit of a kludge here to get the all the relevant tokens into the parse action
# # cleanly otherwise the parameter names are overlapped.
# def f(toks):
#     try:
#         return {'date': toks[0], 'ua': toks[1]}
#     except IndexError:
#         return {'date': toks[0], 'ua': None}


# l1Start.addParseAction(f)
# l1End = uaDateOrSeason ^ "unknown" ^ "open"
# l1End.addParseAction(f)

# level1Interval = l1Start("lower") + "/" + l1End("upper")
# Level1Interval.set_parser(level1Interval)

# # (* *** unspecified *** *)
# yearWithOneOrTwoUnspecifedDigits = Combine(
#     digit + digit + (digit ^ 'u') + 'u'
# )("year")
# monthUnspecified = year + "-" + L("uu")("month")
# dayUnspecified = yearMonth + "-" + L("uu")("day")
# dayAndMonthUnspecified = year + "-" + L("uu")("month") + "-" + L("uu")("day")

# unspecified = yearWithOneOrTwoUnspecifedDigits \
#     ^ monthUnspecified \
#     ^ dayUnspecified \
#     ^ dayAndMonthUnspecified
# Unspecified.set_parser(unspecified)

# # (* *** uncertainOrApproxDate *** *)

# uncertainOrApproxDate = date('date') + UASymbol("ua")
# UncertainOrApproximate.set_parser(uncertainOrApproxDate)

# level1Expression = uncertainOrApproxDate \
#     ^ unspecified \
#     ^ level1Interval \
#     ^ longYearSimple \
#     ^ season

# # (* ************************** Level 2 *************************** *)

# # (* ** Internal Unspecified** *)

# digitOrU = Word(nums + 'u', exact=1)

# # 2-digit day with at least one 'u' present
# dayWithU = Combine(
#     ("u" + digitOrU) ^
#     (digitOrU + 'u')
# )("day")

# # 2-digit month with at least one 'u' present
# monthWithU = Combine(
#     oneOf("0u 1u") ^
#     ("u" + digitOrU)
# )("month")

# # 4-digit year with at least one 'u' present
# yearWithU = Combine(
#     ('u' + digitOrU + digitOrU + digitOrU) ^
#     (digitOrU + 'u' + digitOrU + digitOrU) ^
#     (digitOrU + digitOrU + 'u' + digitOrU) ^
#     (digitOrU + digitOrU + digitOrU + 'u')
# )("year")

# yearMonthWithU = (
#     (Combine(year("") ^ yearWithU(""))("year") + "-" + monthWithU) ^
#     (yearWithU + "-" + month)
# )

# monthDayWithU = (
#     (Combine(month("") ^ monthWithU(""))("month") + "-" + dayWithU) ^
#     (monthWithU + "-" + day)
# )

# yearMonthDayWithU = (
#     (yearWithU + "-" + Combine(month("") ^ monthWithU(""))("month") + "-" + Combine(day("") ^ dayWithU(""))("day")) ^
#     (year + "-" + monthWithU + "-" + Combine(day("") ^ dayWithU(""))("day")) ^
#     (year + "-" + month + "-" + dayWithU)
# )

# partialUnspecified = yearWithU ^ yearMonthWithU ^ yearMonthDayWithU
# PartialUnspecified.set_parser(partialUnspecified)

# # (* ** Internal Uncertain or Approximate** *)

# # this line is out of spec, but the given examples (e.g. '(2004)?-06-04~')
# # appear to require it.
# year_with_brackets = year ^ ("(" + year + ")")

# # second clause below needed Optional() around the "year_ua" UASymbol, for dates
# # like '(2011)-06-04~' to work.

# IUABase = \
#     (year_with_brackets + UASymbol("year_ua") + "-" + month + Optional("-(" + day + ")" + UASymbol("day_ua"))) \
#     ^ (year_with_brackets + Optional(UASymbol)("year_ua") + "-" + monthDay + Optional(UASymbol)("month_day_ua")) \
#     ^ (
#         year_with_brackets + Optional(UASymbol)("year_ua") + "-(" + month + ")" + UASymbol("month_ua") +
#         Optional("-(" + day + ")" + UASymbol("day_ua"))
#     ) \
#     ^ (
#         year_with_brackets + Optional(UASymbol)("year_ua") + "-(" + month + ")" + UASymbol("month_ua") +
#         Optional("-" + day)
#     ) \
#     ^ (yearMonth + UASymbol("year_month_ua") + "-(" + day + ")" + UASymbol("day_ua")) \
#     ^ (yearMonth + UASymbol("year_month_ua") + "-" + day) \
#     ^ (yearMonth + "-(" + day + ")" + UASymbol("day_ua")) \
#     ^ (year + "-(" + monthDay + ")" + UASymbol("month_day_ua")) \
#     ^ (season("ssn") + UASymbol("season_ua"))

# partialUncertainOrApproximate = IUABase ^ ("(" + IUABase + ")" + UASymbol("all_ua"))
# PartialUncertainOrApproximate.set_parser(partialUncertainOrApproximate)

# dateWithInternalUncertainty = partialUncertainOrApproximate \
#                               ^ partialUnspecified

# qualifyingString = Regex(r'\S')  # any nonwhitespace char

# # (* ** SeasonQualified ** *)
# seasonQualifier = qualifyingString
# seasonQualified = season + "^" + seasonQualifier

# # (* ** Long Year - Scientific Form ** *)
# positiveInteger = Combine(positiveDigit + ZeroOrMore(digit))
# longYearScientific = "y" + Combine(Optional("-") + positiveInteger)("base") + "e" + \
#     positiveInteger("exponent") + Optional("p" + positiveInteger("precision"))
# ExponentialYear.set_parser(longYearScientific)

# # (* ** level2Interval ** *)
# level2Interval = (dateOrSeason("lower") + "/" + dateWithInternalUncertainty("upper")) \
#                  ^ (dateWithInternalUncertainty("lower") + "/" + dateOrSeason("upper")) \
#                  ^ (dateWithInternalUncertainty("lower") + "/" + dateWithInternalUncertainty("upper"))
# Level2Interval.set_parser(level2Interval)

# # (* ** Masked precision ** *)
# maskedPrecision = Combine(digit + digit + ((digit + "x") ^ "xx"))("year")
# MaskedPrecision.set_parser(maskedPrecision)

# # (* ** Inclusive list and choice list** *)
# consecutives = (yearMonthDay("lower") + ".." + yearMonthDay("upper")) \
#     ^ (yearMonth("lower") + ".." + yearMonth("upper")) \
#     ^ (year("lower") + ".." + year("upper"))
# Consecutives.set_parser(consecutives)

# listElement = date \
#     ^ dateWithInternalUncertainty \
#     ^ uncertainOrApproxDate \
#     ^ unspecified \
#     ^ consecutives

# earlier = ".." + date("upper")
# EarlierConsecutives.set_parser(earlier)
# later = date("lower") + ".."
# LaterConsecutives.set_parser(later)

# listContent = (earlier + ZeroOrMore("," + listElement)) \
#     ^ (Optional(earlier + ",") + ZeroOrMore(listElement + ",") + later) \
#     ^ (listElement + OneOrMore("," + listElement)) \
#     ^ consecutives

# choiceList = "[" + listContent + "]"
# OneOfASet.set_parser(choiceList)

# inclusiveList = "{" + listContent + "}"
# MultipleDates.set_parser(inclusiveList)

# level2Expression = partialUncertainOrApproximate \
#                    ^ partialUnspecified \
#                    ^ choiceList \
#                    ^ inclusiveList \
#                    ^ maskedPrecision \
#                    ^ level2Interval \
#                    ^ longYearScientific \
#                    ^ seasonQualified

# # putting it all together
# edtfParser = level0Expression("level0") ^ level1Expression("level1") ^ level2Expression("level2")


def parse_edtf(str, fail_silently=False):
    if not str:
        raise EDTFParseException('You must supply some input text')
    str = str.strip()

    # level 0
    try:
        return edtf_parser.match(str).value()
    except pe._errors.ParseError as e:
        raise EDTFParseException(e)
    # if m:= re_date.match(str):
    #     return Date(year=m.group('year'), month=m.group('month'), day=m.group('day'))
    # if m:= re_date_and_time.match(str):
    #     return DateAndTime(
    #         date=Date(year=m.group('year'), month=m.group('month'), day=m.group('day')),
    #         time=m.group('time'),
    #     )
    # if m:= re_l_0_interval.match(str):
    #     return Interval(
    #         lower=Date(year=m.group('year_lower'), month=m.group('month_lower'), day=m.group('day_lower')),
    #         upper=Date(year=m.group('year_upper'), month=m.group('month_upper'), day=m.group('day_upper')),
    #     )

    # # level 1
    # if m:= re_uncertain_or_approximate_date.match(str):
    #     return UncertainOrApproximate(
    #         date=Date(year=m.group('year'), month=m.group('month'), day=m.group('day')),
    #         ua=UA(ua=m.group('ua')),
    #     )
    # if m:= re_unspecified.match(str):
    #     return Unspecified(year=m.group('year'), month=m.group('month'), day=m.group('day'))
    # if m:=re_l_1_interval.match(str):
    #     ends = {}
    #     for end in ['lower', 'upper']:
    #         if m.group(f'year_{end}') is None:
    #             if m.group(f'open_{end}') is not None:
    #                 ends[end] = UncertainOrApproximate(date=m.group(f'open_{end}'))
    #             else:
    #                 ends[end] = UncertainOrApproximate()
    #         else:
    #             ends[end] = UncertainOrApproximate(
    #                 date=Date(year=m.group(f'year_{end}'), month=m.group(f'month_{end}'), day=m.group(f'day_{end}')),
    #                 ua=UA(ua=m.group(f'ua_{end}')),
    #             )
    #     return Level1Interval(lower=ends['lower'], upper=ends['upper'])
    # if m:=re_long_year_simple.match(str):
    #     return LongYear(year=m.group('year'))
    # if m:=re_season.match(str):
    #     return Season(year=m.group('year'), season=m.group('season'))

    # if fail_silently:
    #     return None
    # raise EDTFParseException('Invalid Extended Date/Time Format')


    # try:
    #     if not str:
    #         raise ParseException("You must supply some input text")
    #     p = edtfParser.parseString(str.strip(), parseAll)
    #     if p:
    #         return p[0]
    # except ParseException as e:
    #     if fail_silently:
    #         return None
    #     raise EDTFParseException(e)
