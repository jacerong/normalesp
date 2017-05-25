#!/usr/bin/perl -w

#$w = "áàéèíìóòúùÁÀÉÈÍÌÓÒÚÙçÇñÑâêîôûÂÊÎÔÛäëïöüÄËÏÖÜãẽĩõũÃẼĨÕŨøØæ" ;
#$W = "\.\,\;\:\-\«\»\"\'\&\%\+\=\~\$\@\#\|\(\)\<\>\!\¡\?\¿\\[\\]";


$separador = "<\/article>\n" ;

$/ = $separador;


########Language dependent###################
$LAST = "Véxase tamén|Ligazóns externas|See also|External links|Ver também|Ligações externas|Véase también|Enlaces externos|Voir aussi|Liens externes";
#######Language dependent###################


$ext = "png|gif|jpg|pdf";

while ($article = <STDIN>) {


  #($links) = ($article =~ /<links>([^<>]+)<\/links>/);
  ##extraction of the wiki section: 
 

   ($plaintext) = ($article);
   #if (defined $plaintext) {  


   ##changes to plain text:

   #remove end:
   $plaintext =~ s/[=]+[ ]*[\{]*($LAST)[\}]*[ ]*[=]+[\w\W ]+$//;

   
   #remove weird patterns:
   $plaintext =~ s/\{\{pp-[^}]+\}\}//g;


   #clean [[link]] without |
   $plaintext =~ s/\[\[([^:^\|^\]]+)\]\]/$1/g;
   
   
   #clean [[link|link]]  [[link (..)|link]]
   $plaintext =~ s/\[\[[^:^\|^\]]+\|([^:^\|^\]]+)\]\]/$1/g;

   #clean ''expr'' (italize), '''expr''' (bold), '''''expr''''' (it+bold)
    $plaintext =~ s/['']+([^\']+)['']+/$1/g;
 

   #remove other links [[...]]: trash
   $plaintext =~ s/\[\[[^\]]+\]\][\n]*//g;
  
   
   #clean {{link}} and place with the follwing paragraph plus ":"
   $plaintext =~ s/\{\{([^:^\|^}]+)\}\}[\n]*/$1: /g;

   #clean {{link|link}}
   $plaintext =~ s/\{\{[^:^\|^}]+\|([^:^\|^}]+)\}\}[\n]*/$1: /g;
   
   #remove remaining {{links}}: trash
   $plaintext =~ s/\{\{([^}]+)\}\}//g;


   #clean titles (place with the following paragraph plus ":")
    $plaintext =~ s/[=]+[ ]*([^\=]+)[ ]*[=]+[\n]*/$1\: /g;

   #lists
   #$plaintext =~ s/[\n ]+\*\*\*\*/ ----/g;
   #$plaintext =~ s/[\n ]+\*\*\*/ ---/g;
   #$plaintext =~ s/[\n ]+\*\*/ --/g;
   #$plaintext =~ s/[\n ]+\*/ -/g;
  # $plaintext =~ s/[\n]+([\:\#])/ - /g;
   #$plaintext =~ s/(\-)([^\n\ ])/$1 $2/g;
  
   $plaintext =~ s/[\n ]+(\*)/ $1/g;
   $plaintext =~ s/[\n]+([\:\#])/ * /g;
   $plaintext =~ s/(\*)([^\n\* ])/$1 $2/g;


   #change "----" by newline
   $plaintext =~ s/----[-]*/\n/g;

   #html tags
   $plaintext =~ s/<ref[^>]*>[^<^>]+<\/ref>/ /g;
   $plaintext =~ s/<div[^>]*>[^<^>]+<\/div>/ /g;
   $plaintext =~ s/<[^>]+>//g;
  
   #old versions of links:
    $plaintext =~ s/\[http:[^\]]+\]//g;
   
   #remove user data:
   $plaintext =~ s/[\~\~\~]+//g;

   #remove tables and text inside:
   $plaintext =~ s/[{]*\|[^}]+[}]+//g;

   #clean comments
   $plaintext =~ s/<\!\-\-//g;
   $plaintext =~ s/\-\-\>//g ;
   
   #remove empty lists
   $plaintext =~ s/\*[ ]+\*//g;
   #remove empty parantheses
   $plaintext =~ s/\(\)//g;
   #remove " == "
   $plaintext =~ s/([ ]+)==[=]*([ ]+)/$1$2/g;

   ##remove image files (extensions .png, gif,...)
   $plaintext =~ s/[^ ]+\.($ext)[\|\:]*//ig;  
   $plaintext =~ s/Image:[^\n]+\n/ /g;  

   #######Language dependent###################
   #ad hoc errors:
   $plaintext =~ s/(Ficheiro|File|Fichero|Fichier):[^\n]+\n/ /g;
   #######Language dependent###################


   
 print "$plaintext\n";
 #}
}
