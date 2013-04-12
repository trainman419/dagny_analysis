#!/bin/bash

for d in grass loop out-and-back static waypoints
do
  pushd $d
  ../extract_bag.py ../settings.yaml $d.bag
  popd
done
