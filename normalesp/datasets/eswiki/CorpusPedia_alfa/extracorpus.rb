# Extrai do corpus, para todos os items, um tag dado
# Extract from one corpus, for each item a given tag

if ARGV[0].nil? or STDIN.nil?
	puts "Standard inpunt or firt argument not given. Follow this example:"
	puts "cat glwiki.xml | ruby extracorpus.rb plaintext"
	exit
end

@tag = ARGV[0]

STDIN.each_line("</article>") { |line|
	begin
		part = line.split("</#{@tag}>")[0]
    part = part.split("<#{@tag}>")[1]
    puts part
  rescue
  	#nothing
  end
}



