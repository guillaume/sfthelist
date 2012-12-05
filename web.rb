require 'sinatra'
require './sfthelist'

# generate the file at startup time
SFTHELIST_ICS = "sfthelist.ics"

def generate
  print "Fetching #{SFTHELIST_REMOTE_URL}"
  list = List.new(SFTHELIST_REMOTE_URL)
  return list.calendar.to_s
end

unless File.exists?(SFTHELIST_ICS)
  File.open(SFTHELIST_ICS, 'w') { |file| file.write(generate) }
  print "Successfully wrote #{SFTHELIST_ICS}"
end

get '/' do
  "Everything's A-OK... DO A BARREL ROLL"
end


get "/#{SFTHELIST_ICS}" do
  File.read(SFTHELIST_ICS)
end

