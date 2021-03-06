# Define a estrutura de pastas

LOG_FOLDER = "../log/"
SRC_FOLDER = "../src/"
CORPUS_FOLDER = "../corpus/"
DATA_FOLDER = "../data/"
ONTOLOGY_FOLDER = "../ontology/"
COMPARABLE_FOLDER = "../comparable/"

# If LOG_DIRECTORY doesn't exist, creates. Then open
if not File::exist? LOG_FOLDER
	Dir.mkdir(LOG_FOLDER)
end

# If SRC_DIRECTORY doesn't exist, creates. Then open
if not File::exist? SRC_FOLDER
	Dir.mkdir(SRC_FOLDER)
end

# If CORPUS_DIRECTORY doesn't exist, creates. Then open
if not File::exist? CORPUS_FOLDER
	Dir.mkdir(CORPUS_FOLDER)
end

# If DATA_DIRECTORY doesn't exist, creates. Then open
if not File::exist? DATA_FOLDER
	Dir.mkdir(DATA_FOLDER)
end

# If ONTOLOGY_DIRECTORY doesn't exist, creates. Then open
if not File::exist? ONTOLOGY_FOLDER
	Dir.mkdir(ONTOLOGY_FOLDER)
end

# If COMPARABLE_FOLDER_DIRECTORY doesn't exist, creates. Then open
if not File::exist? COMPARABLE_FOLDER
	Dir.mkdir(COMPARABLE_FOLDER)
end

# Know what files are in the folder
def my_ls(folder)
	# Iterate the entries of the source directory (like ls), create the objects with that info and put it into the array
	sources = Array.new
	Dir.open(folder).each do |entry|
		if entry == "." || entry == ".." || entry[-1..-1] == "~"
			next
		end
		sources << entry
	end
	sources
end
