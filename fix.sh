git pull
jq -M 'del(.metadata.widgets)' movie_reviews.ipynb > movie_reviews2.ipynb 
mv movie_reviews2.ipynb movie_reviews.ipynb
git commit -a -m "Remove widgets from Colab"
git push