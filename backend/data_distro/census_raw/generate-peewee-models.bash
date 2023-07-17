#!/bin/bash

mkdir -p models

tables=("ELECAUDITHEADER" "ELECAUDITFINDINGS" "ELECAUDITS" "ELECCAPTEXT" "ELECCPAS" "ELECEINS" "ELECFINDINGSTEXT" "ELECNOTES")
for t in ${tables[@]}; 
do
    pwiz -H localhost -p 5432 -u postgres -e postgresql -t ${t} -o postgres >>  models/${t}.py
done

dissem=("captext federalaward finding findingtext genauditor general note passthrough revision")
for t in ${dissem[@]}; 
do
    pwiz -H localhost -p 5432 -u postgres -e postgresql -t "dissemination_${t}" -o postgres >>  models/${t}.py
done
