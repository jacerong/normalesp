# Descarrega as últimas versões das wikipedias gl, pt, es, en, fr e executa a aplicação corpuspedia

require "rubygems"
require "open-uri"
require "hpricot"
require 'lib/gerenciador_pastas' # LOG_FOLDER, SRC_FOLDER, CORPUS FOLDER


# Lista de linguas que nos instesam
LANG = ["gl",	"pt", "es", "en", "fr"]
#LANG = []
URL = "http://download.wikimedia.org/#wiki/"

# Lista de enderecos para a descarregas das versoes ajeitadas e mais recentes
enderecos = Hash.new

# Apanha os enderecos finais
LANG.each do |lingua|
	# Criamos a ulr
	url = URL.sub("#",lingua)
	
	# Procuramos por a página do ultimo dump (apanhamos o todos os links e ficamos com o penúltimo)
	doc = Hpricot(open(url))
	links = Array.new
	(doc/"a").each do |link|
	 links << link.attributes['href']
	end
	page_dump = url + links.sort[-2]

	# Procuramos pelo dump "pages-articles" que é o que tem a informação que precisamos
	doc = Hpricot(open(page_dump))
	link_page_article = ""
	(doc/"a").each do |link|
		link_page_article = link.attributes['href']   if (link.attributes['href'] =~ /pages-articles/) != nil
	end
	enderecos[lingua] = link_page_article
end

# Descarrega e descompacta as wikipedias
Dir.chdir(SRC_FOLDER)
enderecos.each do |lingua, url|
	ti = Time.now
	puts "A descarregar a wikipedia em #{lingua} (#{url})"
	system "wget #{url}"
	sleep(3)
	puts "A descompactar a wikipedia em #{lingua}"
	system "bunzip2 #{url.split("/")[-1]}"
	puts "Demora:  " + ((Time.now-ti)/60).to_i.to_s + " (min)"
end

	
# Executar descarregas
#Dir.chdir(__FILE__) Da erro

