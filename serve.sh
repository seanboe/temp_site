cd ./_scripts/

for file in *; do 
  python3 $file
done

cd ../

bundle exec jekyll serve