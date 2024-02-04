# What does it do?
Given a file of SNOMED CT codes that have been promoted to the International version of SNOMED CT
and a file containing ValueSet URLS, check the ValueSet to see which SNOMED CT concepts have been promoted (if any)


# How to use this script

### Set up a python virtual environment
from (https://programwithus.com/learn/python/pip-virtualenv-mac)

```
    git clone https://github.com/mjosborne1/au-in-si
    cd au-in-si
    pip install virtualenv
    virtualenv env
    source env/bin/activate
```

### Create a file of SCT AU codes that were promoted to SI
e.g. /data/sctau-in-si.txt 
contains
```
   32570691000036108 
   32570681000036106
   1586771000168103
   1584731000168109
   1479971000168109
   1418361000168101
   1293061000168108
...
```

### Create a file of ValueSet URLs - these will be used to validate the SCT AU codes 
e.g. /data/ncts-vs.txt
contains
```
    https://healthterminologies.gov.au/fhir/ValueSet/adverse-reaction-agent-1
    https://healthterminologies.gov.au/fhir/ValueSet/assertion-of-absence-1
    https://healthterminologies.gov.au/fhir/ValueSet/australian-medication-1
    https://healthterminologies.gov.au/fhir/ValueSet/body-site-1
....
```

To run the script, Pass these in as parameters to main.py

e.g.
```
   python main.py -u /data/ncts-vs.txt -s /data/sctau-in-si.txt > ./output.txt
```

### Full help 
run python main.py -h

```
   usage: main.py [-h] [-u URLFILE] [-s SCTFILE]

   optional arguments:
     -h, --help            show this help message and exit
     -u URLFILE, --urlfile URLFILE
                           file of valueset urls
     -s SCTFILE, --sctfile SCTFILE
                           file of SNOMED CT codes

```
