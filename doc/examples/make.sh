for file in generate-*
do
        outfile=$(echo $file | sed 's|generate-||' | sed 's|.sh$|.txt|')
        poetry run bash $file > $outfile 2>&1
done

