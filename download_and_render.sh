#!/bin/bash
rm render_output/*.png
rsync -aP nathan@radio-telescope.local:/home/nathan/little-ear-radio-telescope/data/ $1
python3 render_analysis.py --data $1
#ffmpeg -y -r 15 -f image2 -i render_output/%04d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p data_movie.mp4
ffmpeg -y -r 15 -pattern_type glob -i 'render_output/*.png' -pix_fmt yuv420p -c:v libx264 out.mp4
