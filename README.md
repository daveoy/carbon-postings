# postings

## how it works

- postings.py is a library of two classes, Source and Transcode
- these objects describe the state of a source and its dependent transcode
- each Source object has a Transcode child at source.output
- sources.py will scan a job tree for sources in the proper format
- for each source it will check if the dependent transcode exists and submit a kubernetes job to run that source's transcode() method if not

## quirks

- in gitlab-ci.yml you'll see we rebuild both containers if postings.py changes -- we need to use exact image tags rather than relying on latest to make sure the most up to date version of the source and transcode classes are in play
- ~this means we need to update sources.py with any new transcode container image tags as well as update postings.yaml with new source tags (see TODO below)~
- pods are limited to 20 by ResourceQuota in the postings namespace to keep the rushing herd at bay.

## stats

- at steady state sync loops take about 60 seconds, 30 seconds of that is sleeping
- with 1000+ jobs in the queue, sync loops take 1800 seconds. this could be helped by splitting sources runs out per job from a top-level, scan loop.

## TODO

- add scan.py which will submit separate, parallel sources.py jobs to speed up sync loops
- ~replace sources.py transcode container image with env var, let flux update image tag env var?~