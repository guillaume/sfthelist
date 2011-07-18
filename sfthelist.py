import re
from datetime import datetime, date, timedelta
import pytz

PACIFIC_TIMEZONE = pytz.timezone("US/Pacific")

# we need a datetime object at the beginning of the day. datetime.today does not work for that
def morning_datetime(date_obj):
  return datetime(date_obj.year, date_obj.month, date_obj.day, tzinfo=PACIFIC_TIMEZONE ) 


TODAY = date.today()
THIS_MORNING = morning_datetime(date.today())

# CURRENT_YEAR = date.today().year

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

WEEKDAYS = ['sun', 'mon', 'tue', 'wed', 'thr', 'fri', 'sat']
AGES = ['a/a', '?/?', '\d{1,2}\+']




# jun 10 fri Buzzcocks, Images at Slim's, S.F. 6+ $35 9pm *** @ $ (KUSF)
# jun 10 fri Carlos Varela
#        at the Great American Music Hall, S.F. 6+ $25 8pm/9pm **
# jun 10 fri Farewell Continental, Gold Motel, Here Come The Saviours
#        at the Bottom of the Hill, S.F. a/a $13/$15 8:30pm/9pm **
# jun 10 fri Avenue Saints, The Mengz, Culo A Boca at Sub-Mission Gallery, S.F.
#        a/a 8pm ** (also June 11th - Gore Noir Magazine release)
# jun 10 fri Extra Action Electric Marching Band, Itchy-O Marching Band,
#        Tiger Honey Pot, Amnesia Babies, The Burning Wigs Of Sedition
#        at the Rickshaw Stop, S.F. a/a **
# jun 10 fri Palms Spring at Lake Gallery, 661 Divisadero at Grove, S.F.
#        a/a free 7pm * (reception for visual artist Naomi Vanderkindren)
# jun 10 fri Philip Huang, TT Baum, George Birimisa, Cassandra Gorgeous,
#        Cyd Nova, Kirk Read
#        at Center for Sex and Culture, S.F. ?/? $12-$25 8pm ** (day 2)
# jun 10/11/12  PRIMUS (sun), The Flaming Lips (sat),
#        Michael Franti & Spearhead (fri), G. Love & Special Sauce,
#        Grace Potter & The Nocturnals, Edward Sharpe & The Magnetic Zeros,
#        Railroad Earth, Krishna Das With Natacha Atlas & Tiraline,
#        Ghostland Observatory, lost At Last Tribe, Soja, Rootz Underground,
#        David Starfire Ensemble, Gaudi, Opiuo, Shimshai,
#        Moon Alice And David Nelson Band, Luminesque, Visionary Alliance,
#        The Soft White Sixties, El Radio Fantastique, Three Legged Sister,
#        Mike Farrell, Mariel Hemingway & Bobby Williams, John & Ocean Robbins,
#        Will Durst, Caroline Casey, James Twyman, Dr. Steven Greer,
#        Mahendra Kumar Trivedi at the Harmony Festival, Fairgrounds, Santa Rosa
#        a/a $138-$374 (3 day passes) $52 (1 day pass) # **** @
# jun 30-jul 3  My Morning Jacket, Ween, Neko Case, Warren Haynes Band,
#        Yonder Mountain String Band, Rebelution, Gillian Welch, Maceo Parker,
#        Dr. Dog, Chris Robinson Brotherhood, ALO, Beats Antique,
#        Ivan Neville's Dumpstaphunk, Ernest Ranglin, Rebirth Brass Band,
#        Bill Frisell's Beautiful Dreamers, The Travelin' McCourys,
#        Los Amigos Invisibles, Delta Spirit, The Infamous Stringdusters, Dawes,
#        Ruthie Foster, MarchFourth Marching Band, Pimps Of Joytime, Emancipator,
#        Big Gigantic, Danny Barnes, Nathan Moore, Orgone,
#        Jacob Fred Jazz Odyssey, Spanish Bombs, Materialized, Toubab Krewe, Oka,
#        Zach Deputy, Gary Clark Jr.,
#        Youssoupha Sidibe And The Mystic Rhythms Band, Morning Teleportation,
#        Jessica Lurie Ensemble, The Sweetback Sisters,
#        Nicki Bluhm And The Gramblers, The Soft White Sixties, Mia Dyson,
#        Head For The Hills, Elephant Revival, Zoe Keating,
#        He's My Brother She's My Sister, Diego's Umbrella, The Congress, MaMuse,
#        Dead Winter Carpenters, The Brothers Comatose, Rebecca Loebe, Tracorum,
#        Living Folklore, Banana Slug String Band, Skerik, Josh Clark,
#        Audio Angel at High Sierra Music Festival, Quincy a/a ***
# jul  4-6   George Clinton & Parliament Funkadelic
#        at Yoshi's, 510 Embarcadero West, Oakland ?/? ***


class UnableToParseList(Exception):
  def __init__(self, value):
      self.value = value
  def __str__(self):
      return repr(self.value)

class Event:
  
  def month_abbr_to_decimal(self, abbr):
    return datetime.strptime(abbr, "%b").month
    
  def __init__(self, *args, **kwargs):
    self.dates = []
    month = kwargs.get('month', None)
    days = kwargs.get('days', None)
    
    month_start = kwargs.get('month_start', None)
    day_start = kwargs.get('day_start', None)
    month_end = kwargs.get('month_end', None)
    day_end = kwargs.get('day_end', None)
    
    self.rest = kwargs.get('rest', "")
    
    
    # process month and day(s)
    if month and days:
      days = self.parse_days(days)
      for day in days: 
        proposed_date = datetime(TODAY.year, self.month_abbr_to_decimal(month), int(day), tzinfo=PACIFIC_TIMEZONE)
        if proposed_date < THIS_MORNING:
          proposed_date.replace(year=proposed_date.year+1)
        self.dates.append(proposed_date)

    # process date range
    elif month_start and day_start and day_end:
      if month_end == None:
        month_end = month_start
      proposed_start_date = datetime(TODAY.year, self.month_abbr_to_decimal(month_start), int(day_start), tzinfo=PACIFIC_TIMEZONE)
      if proposed_start_date < THIS_MORNING:
        proposed_start_date.replace(year=proposed_start_date.year+1)
      
      proposed_end_date = datetime(proposed_start_date.year, self.month_abbr_to_decimal(month_end), int(day_end), tzinfo=PACIFIC_TIMEZONE)
      
      if(proposed_end_date < proposed_start_date):
        raise UnableToParseList("end_date < start_date: %s %s - %s %s" % (month_start, day_start, month_end, day_end))
        
      while proposed_start_date <= proposed_end_date:
        self.dates.append(morning_datetime(proposed_start_date))
        proposed_start_date += timedelta(days=1)
      
 
  def parse_days(self, days):
    return [int(day) for day in days.split('/')]
    
  def __str__(self):
    
    return """Dates : %s
Description : %s
    """ % (', '.join([str(e) for e in self.dates]), self.rest)
    


    


months = '|'.join(MONTHS)
weekdays = '|'.join(WEEKDAYS)
regex1 = '(%s)\s+(\d{1,2}) (%s)(.*)' % (months, weekdays) # matches : jun 10 fri ...
regex2 = '(%s)\s+([\d/]+) (.*)' % (months) # matches : jun 10/11/12 ...
regex3 = '(%s)\s+([\d]+)-((%s)\s+)?([\d]+) (.*)' % (months, months) # matches : jul  4-6  and jun 30-jul 3 ...


class List:
  
  """Parses sfthelist file"""
  def __init__(self, f):
    self.events = []
    for l in f:

      mo1 = re.match(regex1, l)
      mo2 = re.match(regex2, l)
      mo3 = re.match(regex3, l)

      # print 'mo1', mo1
      # print 'mo2', mo2
      if mo1 or mo2 or mo3:

        if mo1:
          month, days, weekday, rest = mo1.groups()
          event = Event(month=month, days=days, rest=rest)
          
        elif mo2:
          month, days, rest = mo2.groups()
          event = Event(month=month, days=days, rest=rest)
          
        elif mo3:
          print mo3.groups()
          month_start, day_start, month_end_group, month_end, day_end, rest = mo3.groups()
          event = Event(month_start=month_start, day_start=day_start, month_end=month_end, day_end=day_end, rest=rest)

        self.events.append(event)
      else:
        event.rest += ' ' + l.rstrip('\n').lstrip(' ')
    
  def __str__(self):
    return '\n'.join([str(event) for event in self.events])






print List(open('testcase.txt'))


# for event in events:
#   print event
#   time.sleep(1)
  

  
  # regex = '(%s) (\d{1,2}) (%s).*?(at( the)?)(.*?)' % (months, weekdays)
  # m = re.search(regex,l)
  # print m