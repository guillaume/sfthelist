require "rubygems"
require "polyglot"
require "treetop"
require "pp"
require "active_support/all"
require "ri_cal"
require 'open-uri'

require "./sfthegrammar"

SFTHELIST_REMOTE_URL = 'http://jon.luini.com/thelist/thelist.txt'
class NewYearStateMachine
  
  attr_reader :year_addition
  def initialize
    @year_addition = 0
    @date = nil
  end
  
  def set_date(date)
    
    if !@date.nil? and (@date.month > date.month)
      @year_addition += 1
    end
    @date = date
  end
end

class Event
  @@new_year_state_machine = NewYearStateMachine.new
  @@parser = SFTheListParser.new
  attr_reader :date, :bands, :venue, :age_restriction, :price, :time, :annotations, :annotations_text, :first_hour
  DEFAULT_TIME = "5pm" # reasonable time for a show with unknown hour
  
  def clean_string(string)
    return string.gsub(/\s+/, " ").strip
  end
  def clean_time(time)
    time.gsub("noon", "12pm").gsub("midnight","11:59pm")
  end
  # sanitize the parse objects into clean values
  def initialize(parse_objects)
    # p parse_objects
    parse_objects.each do |o|
      if o.kind_of?(Array) and o.size == 2
        key = o[0]
        value = o[1]
        case key
          
        # Parse the first day of the date
        when :date
          first_day = @@parser.parse(value, :consume_all_input => false, :root => :first_day)
          raise "Failed to parse first day" unless !first_day.nil?
          @date = Time.parse(first_day.text_value)
          @@new_year_state_machine.set_date(@date)
          @date += @@new_year_state_machine.year_addition.year
        # Remove extraneous spaces from bands
        when :bands
          @bands = clean_string(value)
        when :venue
          @venue = value
        when :age_restriction
          @age_restriction = value
        when :notes
          notes = clean_string(value)
          price = @@parser.parse(notes, :consume_all_input => false, :root => :price)
          @price = price.text_value unless price.nil?
          
          @@parser.parse(notes, :consume_all_input => false, :root => :whitespace, :index => @@parser.index)
          time = @@parser.parse(notes, :consume_all_input => false, :root => :time, :index => @@parser.index)
          @time = clean_time(time.text_value) unless time.nil?
          
          @@parser.parse(notes, :consume_all_input => false, :root => :whitespace, :index => @@parser.index)
          annotations = @@parser.parse(notes, :consume_all_input => false, :root => :annotations, :index => @@parser.index)
          @annotations = annotations.text_value unless annotations.nil?
          
          if @annotations
            @annotations_text = @annotations.clone
            @annotations_text = @annotations_text.gsub("$", " Will probably sell out. ")
            @annotations_text = @annotations_text.gsub("^", " Under 21 must pay more. ")
            @annotations_text = @annotations_text.gsub("@", " Pit warning. ")
            @annotations_text = @annotations_text.gsub("#", " No ins/outs. ")
            @annotations_text = @annotations_text.gsub(/(\*+)/, ' Recommendable show : \1. ')
            @annotations_text = clean_string(@annotations_text)
          end
          
          if @time
            first_hour = @@parser.parse(@time, :consume_all_input => false, :root => :hour)
            @first_hour = first_hour.text_value unless first_hour.nil?
            # puts @time + " => " + @first_hour

            # parse the date again but with an hint of the start time
            @date = Time.parse(@first_hour, @date)
          else
            # if we failed to get a time, default to a reasonable time for a show
            @date = Time.parse(DEFAULT_TIME, @date)
            
          end

          
        end
        
      end
    end
  end
  
  
  def fill_ical_event(ical_event)
    ical_event.summary = [@bands, @venue].join(" @ ")
    ical_event.description = [@age_restriction, @price, @time, @annotations_text].join("\n")
    ical_event.dtstart =  @date.getutc
    ical_event.dtend = (@date + 1.hour).getutc
    ical_event.location = @venue
  end
end

class List
  attr_reader :calendar
  
  def initialize(url)
    parser = SFTheListParser.new
    
    text = open(url) { |f| f.read }

    text = text.match(/funk-punk-thrash-ska.*?\n\n(.*?)\n\n/m)[1]

    parsetree = parser.parse(text)

    events = []

    # in the case that this returns nil, it means we were unable to parse the list
    raise parser.failure_reason unless parsetree
    events = parsetree.content.map { |e| Event.new(e) }

    @calendar = RiCal.Calendar do |cal|
      events.each do |e|
        cal.event do |ical_event|
          e.fill_ical_event(ical_event)
        end
      end
    end
    
  end
end


def main
  if ARGV.size >= 1
    urls = ARGV
  else
    urls = [SFTHELIST_REMOTE_URL]
  end
  
  urls.each do |url|
    list = List.new(url)
    print list.calendar
  end  
end

if __FILE__ == $0
  main
end
