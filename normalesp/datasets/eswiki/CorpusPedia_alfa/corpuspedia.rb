# coding: utf-8
# EXECUTE IN ruby1.9


# CorpusPedia 1.8
# Isaac Gonzalez
# Extração do Texto da Wikipedia
# Versão 1.8 Engadir o parser de Pablo Wiki2Text

require 'rexml/document'
require 'rexml/parsers/streamparser'
require 'timeout'
require 'date'
require_relative 'lib/gerenciador_pastas' # LOG_FOLDER, SRC_FOLDER, CORPUS FOLDER, DATA FOLDER
#require 'nokogiri'
#include Nokogiri


# Module for create corpus
module Corpus_wiki_item

	# Expression (in the title) that must not be added to the corpus
	DIRTY_EXP = { "gl" => ["Media:", "Especial:", "Conversa:", "Usuario:", "Conversa usuario:", "Wikipedia:", "Conversa Wikipedia:", "Ficheiro:", "Conversa ficheiro:", "MediaWiki:", "Conversa MediaWiki:", "Modelo:", "Conversa modelo:", "Axuda:", "Conversa axuda:", "Categoría:", "Conversa categoría:", "Portal:", "Portal talk:"],
								"pt" => ["Media:", "Especial:", "Discussão:", "Usuário:", "Usuário Discussão:", "Wikipedia:", "Wikipedia Discussão:", "Ficheiro:", "Ficheiro Discussão:", "MediaWiki:", "MediaWiki Discussão:", "Predefinição:", "Predefinição Discussão:", "Ajuda:", "Ajuda Discussão:", "Categoria:", "Categoria Discussão:", "Portal:", "Portal Discussão:", "Anexo:", "Anexo Discussão:"],
								"es" => ["Media:", "Especial:", "Discusión:", "Usuario:", "Usuario Discusión:", "Wikipedia:", "Wikipedia Discusión:", "Archivo:", "Archivo Discusión:", "MediaWiki:", "MediaWiki Discusión:", "Plantilla:", "Plantilla Discusión:", "Ayuda:", "Ayuda Discusión:", "Categoría:", "Categoría Discusión:", "Portal:", "Portal Discusión:", "Wikiproyecto:", "Wikiproyecto Discusión:", "Anexo:", "Anexo Discusión:"],
								"en" => ["Media:", "Special:", "Talk:", "User:", "User talk:", "Wikipedia:", "Wikipedia talk:", "File:", "File talk:", "MediaWiki:", "MediaWiki talk:", "Template:", "Template talk:", "Help:", "Help talk:", "Category:", "Category talk:", "Portal:", "Portal talk:"],
								"fr" => ["Média:", "Spécial:", "Discussion:", "Utilisateur:", "Discussion utilisateur:", "Wikipédia:", "Discussion Wikipédia:", "Fichier:", "Discussion fichier:", "MediaWiki:", "Discussion MediaWiki:", "Modèle:", "Discussion modèle:", "Aide:", "Discussionaide:", "Catégorie:", "Discussion catégorie:", "Portail:", "Discussion Portail:", "Projet:", "Discussion Projet:", "Référence:", "Discussion Référence:"]}

	# Expressions to get related content
	# RELATED = {"lang" => ["First delimiter", "Middle delimiter", "End delimiter"]}
	RELATED = {	"gl" => {"first" => "==Véxase tamén==", "middle" => "===Outros artigos===", "end" => "[[Categoría:"},
							"pt" => {"first" => "== Ver também ==", "middle" => "", "end" => "[[Categoria:"},
							"es" => {"first" => "== Véase también ==", "middle" => "", "end" => "[[Categoría:"},
							"en" => {"first" => "==See also==", "middle" => "", "end" => "[[Category:"},
							"fr" => {"first" => "== Voir aussi ==", "middle" => "", "end" => "[[Catégorie:"},
	}

	# Constructor
	def execute_corpus(title,text)
		@title, @text = title.force_encoding("UTF-8"), text.force_encoding("UTF-8")
		@article = clean_article(@text).chomp.force_encoding("UTF-8")
		@category = extract_categories(@text).force_encoding("UTF-8")
		@related = extract_related(@text).force_encoding("UTF-8")
		@links = extract_links(@text).force_encoding("UTF-8")
		@translations = extract_translations(@text)
		# Print results
		$corpus_file.puts xml_item
		$translations_file.puts print_translations(@translations)
	end

	def xml_item
			"<article>\n\t<title>#{@title}</title>\n\t<category>#{@category}</category>\n\t<related>#{@related}</related>\n\t<links>#{@links}</links>\n\t<translations>#{print_translations(@translations)}</translations>\n\t<plaintext>#{@article}</plaintext>\n\t<wikitext>#{@text}</wikitext>\n</article>\n".force_encoding("UTF-8")
	end

	# Class method
	def Corpus_wiki_item.validate_corpus?(title,artigo)
		# Valida que o título non conteña "Mediawiki:" ou "Categoria" ou ...
		validate = true
		DIRTY_EXP[$lang].each do |exp|
			if title[0...exp.size] == exp
				return false
				# $log_file.puts "Metacontent"
			end
		end

		# Valida que o título non esté valeiro ou comece com REDIRECT ou ...
  	if artigo == "" || artigo[0...8] == "REDIRECT"
	  		# $log_file.puts "Article content empty or incorrect (REDIRECT)"
	  		return false
		end
		true
	end


  private


  # Get the relevant part of text in the proper format
  def clean_article(article)
  	# Erase meta information of the category
  	if article.split(RELATED[$lang]["first"])[0] != nil
			article = article.split(RELATED[$lang]["first"])[0]
		end
		if article.split(RELATED[$lang]["middle"])[0] != nil
			article = article.split(RELATED[$lang]["middle"])[0]
		end
		if article.split(RELATED[$lang]["end"])[0] != nil
			article = article.split(RELATED[$lang]["end"])[0]
		end
		# Trasform wikitext to plaintext with the script
		plaintext = wiki_to_plaintext(article)

  	plaintext
  end

	# Extract categories separated by comma
	def extract_categories(article)
		pat = Regexp.new(RELATED[$lang]["end"].gsub('[','\[') + '([^|\]]+)(\||\]\])') # Pattern to find the categories
		categories = Array.new
		article.each_line do |line|
			categories << pat.match(line)[1] if pat.match(line) != nil
		end
		categories.join(", ")
	end

	# Extract related terms comma separated
	def extract_related(article)
		# Delimitar parte a extraer
		if article.split(RELATED[$lang]["first"])[1] != nil
			article = article.split(RELATED[$lang]["first"])[1]
		elsif RELATED[$lang]["middle"] != "" && article.split(RELATED[$lang]["middle"])[1] != nil
			article = article.split(RELATED[$lang]["middle"])[1]
		else
			return ""
		end
		article = article.split(RELATED[$lang]["end"])[0]
		# Extraer
		pattern = /\*\s?\[\[(.+)(\||\]\])/
		related = Array.new
		article.each_line do |line|
			related << pattern.match(line)[1] if pattern.match(line) != nil
		end
		related.join(", ")
	end

	# Extract the links to another wikipedia article
	def extract_links(article)
		# Extract all the links expression without :
		links = article.scan(/\[\[([^\]:\[*]+)(\])/)
		links = links.collect { |l| l[0] } # We must take the first element of each scan element, because we have to use parenthesis for or element in regexp
		links.join(", ")
	end

	# Get translations in a hash with "lang" => "tranlation" entries
	def extract_translations(cadea)
		trad = Hash.new
		pattern = /\[\[(\w\w):(.+)\]\]/
		cadea.each_line do |cad|
			if pattern.match(cad) != nil
				trad[pattern.match(cad)[1]] = pattern.match(cad)[2]
			end
		end
		trad
	end

	# Print hash translations
	def print_translations(trad)
		# Pattern: gl pt es en fr ca eu al it cs bg el
		trad.default = "#"
		"#{trad["gl"]}\t#{trad["pt"]}\t#{trad["es"]}\t#{trad["en"]}\t#{trad["fr"]}\t#{trad["ca"]}\t#{trad["eu"]}\t#{trad["al"]}\t#{trad["it"]}\t#{trad["cs"]}\t#{trad["bg"]}\t#{trad["el"]}"
	end

	# Transform a strig in wiki format to plaintext format
	def wiki_to_plaintext(wikitext)
		#$w = "áàéèíìóòúùÁÀÉÈÍÌÓÒÚÙçÇñÑâêîôûÂÊÎÔÛäëïöüÄËÏÖÜãẽĩõũÃẼĨÕŨøØæ"
		#$W = "\.\,\;\:\-\«\»\"\'\&\%\+\=\~\$\@\#\|\(\)\<\>\!\¡\?\¿\\[\\]"
		plaintext = wikitext

		#remove weird patterns:
		plaintext = plaintext.gsub(/\{\{pp-[^}]+\}\}/,"")

		#clean [[link]] without |
		plaintext = plaintext.gsub(/\[\[([^:^\|^\]]+)\]\]/,'\1')

		#clean [[link|link]]  [[link (..)|link]]
		plaintext = plaintext.gsub(/\[\[[^:^\|^\]]+\|([^:^\|^\]]+)\]\]/,'\1')

		#clean ''expr'' (italize), '''expr''' (bold), '''''expr''''' (it+bold)
		plaintext = plaintext.gsub(/['']+([^\']+)['']+/,'\1')

		#remove other links [[...]]: trash
		plaintext = plaintext.gsub(/\[\[[^\]]+\]\][\n]*/,"")

		#clean {{link}} and place with the follwing paragraph plus ":"
		plaintext = plaintext.gsub(/\{\{([^:^\|^}]+)\}\}[\n]*/,'\1')

		#clean {{link|link}}
		plaintext = plaintext.gsub(/\{\{[^:^\|^}]+\|([^:^\|^}]+)\}\}[\n]*/,'\1' + ": ")

		#remove remaining {{links}}: trash
		plaintext = plaintext.gsub(/\{\{([^}]+)\}\}/,"")

		#clean titles (place with the following paragraph plus ":")
		plaintext = plaintext.gsub(/[=]+[ ]*([^\=]+)[ ]*[=]+[\n]*/,'\1' + "\: ")

		#lists
		#plaintext = plaintext.gsub(/[\n ]+\*\*\*\*/ ----)
		#plaintext = plaintext.gsub(/[\n ]+\*\*\*/ ---)
		#plaintext = plaintext.gsub(/[\n ]+\*\*/ --)
		#plaintext = plaintext.gsub(/[\n ]+\*/ -)
		# plaintext = plaintext.gsub(/[\n]+([\:\#])/ - )
		#plaintext = plaintext.gsub(/(\-)([^\n\ ])/'\1' $2)

		plaintext = plaintext.gsub(/[\n ]+(\*)/, '\1')
		plaintext = plaintext.gsub(/[\n]+([\:\#])/," * ")
		plaintext = plaintext.gsub(/(\*)([^\n\* ])/,'\1' + '\2')

		#change "----" by newline
		plaintext = plaintext.gsub(/----[-]*/,"\n")

		#html tags
		plaintext = plaintext.gsub(/<ref[^>]*>[^<^>]+<\/ref>/," ")
		plaintext = plaintext.gsub(/<div[^>]*>[^<^>]+<\/div>/," ")
		plaintext = plaintext.gsub(/<[^>]+>/,"")

		#old versions of links:
		plaintext = plaintext.gsub(/\[http:[^\]]+\]/,"")

		#remove user data:
		plaintext = plaintext.gsub(/[\~\~\~]+/,"")

		#remove tables and text inside:
		plaintext = plaintext.gsub(/[{]*\|[^}]+[}]+/,"")

		#clean comments
		plaintext = plaintext.gsub(/\<\!\-\-/,"")
		plaintext = plaintext.gsub(/\-\-\>/,"")

		#remove empty lists
		plaintext = plaintext.gsub(/\*[ ]+\*/,"")
		#remove empty parantheses
		plaintext = plaintext.gsub(/\(\)/,"")
		#remove " == "
		plaintext = plaintext.gsub(/([ ]+)==[=]*([ ]+)/,'\1'+'\2')

		##remove image files (extensions .png, gif,...)
		plaintext = plaintext.gsub(/[^ ]+\.($ext)[\|\:]*/,"")
		plaintext = plaintext.gsub(/Image:[^\n]+\n/," ")

		#######Language dependent###################
		#ad hoc errors:
		plaintext = plaintext.gsub(/(Ficheiro|File|Fichero|Fichier):[^\n]+\n/,"" )
		#######Language dependent###################

		plaintext
	end
end



# Category and ontology module
module Category_wiki_item
	# CATEGORY = {"lang" => "Categoría"}
	CATEGORY = {	"gl" => "Categoría:", "pt" => "Categoria:", "es" => "Categoría:", "en" => "Category:", "fr" => "Catégorie:"}

	# Sem constructor para que as controle a superclasse
	def execute_category(title,text)
		@title, @text = title.split(":")[1], text
		@categories = extract_categories(@text)
		$category_file.puts "#{@title}\t#{@categories}"

		#$tudos[@title] = categories.split(", ")
		#puts @title
	end

	def Category_wiki_item.validate_category?(title,text)
		# Valida no titulo que seja uma categoria
		title[0...CATEGORY[$lang].size] == CATEGORY[$lang]
	end


  private

	# Extract categories separated by comma
	def extract_categories(article)
		pat = /\[\[#{CATEGORY[$lang]}([^|\]]+)(\||\])/ # Pattern to find the categories
		categories = Array.new
		article.each_line do |line|
			categories << pat.match(line)[1] if pat.match(line) != nil
		end
		categories.join(", ")
	end
end


# General module
module Wiki_item
	include Corpus_wiki_item
	include Category_wiki_item

	def execution_all(title,text)
		@title, @text = title, text
		if Corpus_wiki_item.validate_corpus?(@title,@text) and $option_corpus
			@corpus_wiki = Corpus_wiki_item.execute_corpus(@title,@text)
		end
		if Category_wiki_item.validate_category?(@title,@text) and $option_ontology
			@categoy_wiki = Category_wiki_item.execute_category(@title,@text)
		end
	end
end


# Creates an articles listener to handle the events
class ArticlesXMLListener
  def initialize
		@title_buffer = nil
		@title_tag = "title" # xml tag for the title
		@article_tag = "text" # xml tag for the text
  end

  def tag_start(name, attrs)

  end

  def text(text)
    @textbuffer = text
  end

  def tag_end(name)
		if name == @title_tag
			if @title_buffer == nil
				@title_buffer = @textbuffer
			else
				puts "\t####Erro, artigo sem descrição (#{@title_buffer})"
				@title_buffer = @textbuffer
			end
		elsif name == @article_tag
			if @title_buffer != nil

				###   EXECUTAR   ###
				Wiki_item.execution_all(@title_buffer.to_s,@textbuffer)
				### FIM EXECUTAR ###

				@title_buffer = nil
			else
				puts "Erro, artigo sem titulo"
			end
		end
  end
end

=begin
# XML listener for nokogiri
class PostCallbacks < XML::SAX::Document
  def initialize
		@title_buffer = nil
		@title_tag = "title" # xml tag for the title
		@article_tag = "text" # xml tag for the text
  end

  def start_element(element, attributes)
    #puts "************************************" + element
    @textbuffer = ""
  end

  def characters(text)
    @textbuffer += text
  end

  def end_element(element)
		if element == @title_tag
			if @title_buffer == nil
				@title_buffer = @textbuffer
			else
				puts "####Erro, artigo sem descrição (#{@title_buffer})"
				@title_buffer = @textbuffer
			end
		elsif element == @article_tag
			if @title_buffer != nil

				### EXECUTAR     ###
				Wiki_item.execution_all(@title_buffer.to_s,@textbuffer)
				### FIM EXECUTAR ###

				@title_buffer = nil
			else
				puts "Erro, artigo sem titulo"
			end
		end
  end
end
=end


###### INDEX

# Arrumar onde corresponda
include Wiki_item

#  Handle command line parameters
## ruby corpuspediaXX.rb [-c|-o|-co-n] [-rex|-nok] [-lang:l1,l2,l3,...]
puts "usage: ruby corpuspediaXX.rb [-c|-o|-co|-n] [-lang:l1,l2,l3...]"
puts "\t -c corpus only     -o ontology only       -co corpus and ontology  -n nothing"
$option_corpus = true
$option_ontology = true
$parser = "rex"
$option_lang = "todas"

ARGV.each do |item|
	if item[0..-1] == "-c"
		$option_corpus = true
		$option_ontology = false
	elsif item[0..-1] == "-o"
		$option_corpus = false
		$option_ontology = true
	elsif item[0..-1] == "-co"
		$option_corpus = true
		$option_ontology = true
	elsif item[0..-1] == "-n"
		$option_corpus = false
		$option_ontology = false
	elsif item[0..-1] == "-rex"
		$parser = "rex"
	elsif item[0..-1] == "-nok"
		puts "Not avaliable yet"
		$parser = "rex"
	elsif item[0..4] == "-lang"
		$option_lang = item[6..-1].split(",")
	end
end


# Executar a procura
my_ls(SRC_FOLDER).each do |f_entrada|
	next if f_entrada[-4..-1] != ".xml"
	# Language
	$lang = f_entrada[0...2]

	# Test if language must be executed
	next if not $option_lang.include?($lang) and $option_lang != "todas"

	# Create vars (this must be in the class because if only creates a corpus vars for categories is created too and that's worng)
	$lang = f_entrada[0...2]
	$log_file = File.new(LOG_FOLDER + "/" + f_entrada[0..6] + "#{Date.today.to_s}-log.txt","a+")
	$corpus_file = File.new(CORPUS_FOLDER + f_entrada[0..6] + "corpus.txt","w")
	$category_file = File.new(DATA_FOLDER + f_entrada[0..6] + "categories.txt","w")
	$translations_file = File.new(DATA_FOLDER + f_entrada[0..6] + "translations.txt","w")

	# Open file
	source_xml = File.open SRC_FOLDER + f_entrada
	ti = Time.now

	# Execute parser
	if $parser[0..-1] == "rex"
		REXML::Document.parse_stream(source_xml, ArticlesXMLListener.new)
	elsif $parser[0..-1] == "nok"
		nokogiri_parser = XML::SAX::Parser.new(PostCallbacks.new)
		nokogiri_parser.parse_file(SRC_FOLDER + f_entrada)
	else
		puts $log_file.puts "Erro interno na escolha de parser"
	end


	puts "Análise do XML demorou:" + ((Time.now-ti)/60).to_i.to_s + " (min) para: " + f_entrada
	$log_file.puts "Análise do XML demorou:" + ((Time.now-ti)/60).to_i.to_s + " (min) para: " + f_entrada

	# FAZER CLOSE DOS FICHEIROS
	$corpus_file.close
	$log_file.close
	$category_file.close
end
