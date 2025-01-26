#!/bin/sh
cat README_START.md>README.md
python /home/ec2-user/gemtalker/readmdmaker.py get_enphase_hour_measure.py>>README.md
python /home/ec2-user/gemtalker/readmdmaker.py history_collector.py>>README.md
git add README.md
git commit README.md -m regenerated
git push
