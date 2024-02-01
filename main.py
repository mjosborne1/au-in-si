import subprocess
import argparse
import os
import urllib.parse
import json

# Get the ValueSet urls and SNOMED CT codes to check from files
homedir=os.environ['HOME']
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--urlfile", help="file of valueset urls", default=homedir+"/data/ncts-vs.txt")
parser.add_argument("-s", "--sctfile", help="file of SNOMED CT codes", default=homedir+"/data/sctau-in-si.txt")
args = parser.parse_args()
if args.urlfile != "":
   urlfile=args.urlfile

if args.sctfile != "":
   sctfile=args.sctfile

# Open the file with URLs and read into a list
with open(urlfile) as f1:
    urls = f1.read().splitlines()

# Open the SNOMED CT code file and read into a list
with open(sctfile) as f2:
    codes = f2.read().splitlines()

# Set up the base validate-code url
baseurl="https://tx.ontoserver.csiro.au/fhir/ValueSet/$validate-code"
sys="http://snomed.info/sct"

# Iterate through the urls
for url in urls:
   for code in codes:
      code=code.strip()
      query=baseurl+'?url='+urllib.parse.quote(url,safe='')+"&code="+code+"&system="+sys
      # Build the curl command with URL and parameters  
      command = ['curl', '-H "Accept: application/json" ' , '--location', query]
      
      #
      # Call curl subprocess  
      result = subprocess.run(command, capture_output=True)
      nf="was not found in the value set "
      data =  json.loads(result.stdout)
      # Check the valueString value of the last parameter object - assumes it's an error message, if it's not it's probably a match for the SCT AU concept
      check=data['parameter'][-1]['valueString']
      if nf in check:
         print(url+','+code+',Not found')
      else:
         print(url)
         print(result.stdout)
