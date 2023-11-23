#!/bin/bash
echo "Removing duplicates."
fdupes -rdN download/.

echo "Removing empty ones."
find download/ -type f -name "*.mp3" -empty -print -delete

echo "Removing unwanted filetypes."
for file in `find download/ -type f -name "*.mp3"`
do 
	suspect=`file $file | grep -v ": Audio file with ID3 version" | grep -v ": MPEG ADTS, layer III,"`
	if [ -n "$suspect" ]
	then
		not_html=`echo $suspect | grep -v ": HTML document,"`
		if [ -n "$not_html" ]
		then
			echo "Suspect $suspect"
		else
			file_name=`echo $suspect| cut -d ":" -f 1`
			echo "Removing $file_name"
			rm -rf $file_name
		fi
	fi
done
