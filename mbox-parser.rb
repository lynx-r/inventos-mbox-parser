#! /usr/bin/env ruby

require 'optparse'
require 'ostruct'

class MBoxParser

  def initialize
    @name_and_email_dict = {}
  end

  def parse(messages, aliases_list)
    messages.each do |message|
      if message.start_with? 'From: '
        match = message.match(/From: ([a-zA-Z ]+\s+)?<(.*)>/i)
        if match
          name, email = match.captures
          name = name ? name : ''
          if aliases_list.empty?
            simple_parse name, email
          else
            consider_aliases_parse name, email, aliases_list
          end
        end
      end
    end
  end

  def print_result
    @name_and_email_dict.sort_by { |_, value| value[-1] }.each { |key, value|
      puts key + ': ' + value[-1].to_s
    }
  end

  private
  def simple_parse(name, email)
    if @name_and_email_dict.has_key? email
      @name_and_email_dict[email][-1] += 1
    else
      @name_and_email_dict[email] = name, email, 1
    end
  end

  def consider_aliases_parse(name, email, aliases)
    has_aliases = has_aliases email, aliases
    if has_aliases[0]
      key = has_aliases[1]
      if @name_and_email_dict.has_key? key
        @name_and_email_dict[key][-1] += 1
      else
        @name_and_email_dict[key] = key, email, 1
      end
    elsif @name_and_email_dict.has_key? email
      @name_and_email_dict[email][-1] += 1
    else
      @name_and_email_dict[email] = name, email, 1
    end
  end

  def has_aliases(email, aliases)
    aliases.each { |alias_line|
      alias_list = alias_line.split ' '
      if alias_list.include? email
        return TRUE, alias_list[0]
      end
    }
    return FALSE, email
  end
end

if __FILE__ == $0
  messages = []
  line = $stdin.gets
  while line
    messages << line.strip
    line = $stdin.gets
  end

  options = OpenStruct.new
  options.aliases = ''
  opt_parser = OptionParser.new do |opts|
    opts.banner = 'Запуск: cat messages.mbox | mbox-parser.rb [-a aliases.txt]'
    opts.on('-a', '--aliases ALIASES') do |a|
      options.aliases = a
    end
  end
  opt_parser.parse! ARGV

  parser = MBoxParser.new

  aliases_list = []
  unless options.aliases.empty?
    begin
      aliases_list = File.open(options.aliases) { |file| file.readlines }
    rescue
      puts 'Файл с псевдонимами не найден. Выполняем парсинг без учета псевдонимов.'
    end
  end
  parser.parse messages, aliases_list
  parser.print_result
end
