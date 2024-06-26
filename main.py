import subprocess
import argparse
import fetcher
import feedparser
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import json

import os, shutil


# Create the npm file structure and required support files
def build_npm_folder_structure(args):
   """
   Create a folder structure in outdir/
   Level 1: healthterminologies.gov.au@1.0.0
   Level 2: node_modules/  package.json ( dependencies: "healthterminologies.gov.au" )
   Level 3: inside node_modules/ a folder called "healthterminologies.gov.au"
   Level 4: inside healthterminologies.gov.au/ go all the json files
   """
   npm_dir = os.path.join(args.outdir,f"{args.package_name}@{args.package_version}")
   if os.path.exists(npm_dir): 
      shutil.rmtree(npm_dir)
   node_folder = os.path.join(npm_dir,"node_modules",f"{args.package_name}")
   os.makedirs(node_folder)
   pkg = { "dependencies": { args.package_name: f"^{args.package_version}" }}
   json_pkg = json.dumps(pkg, indent=2)
   pkg_filename=os.path.join(npm_dir,"package.json")
   with open(pkg_filename,'w') as pkg_file:
      pkg_file.write(json_pkg)
   return node_folder


# Mainline
# Create an OAuth token using your own client secret codes
# To find your client ID and secret, login to https://www.healthterminologies.gov.au/ and click Clients on the top menu  
# save the Client Id and Secret in an env file along with the syndication server endpoint and other properties
# You are welcome to also use something like a Cloud Secrets Manager see here: https://blog.gitguardian.com/how-to-handle-secrets-in-python/ for more advice
# For more information on implementing Clinical Terminology, see National Clinical Terminology Service
# Guide for Implementers https://www.healthterminologies.gov.au/library/Clinical-Terminology-Implementation-Process-Checklist.pdf and 
# https://ontoserver.csiro.au/docs/6/config-syndication.html#:~:text=Australian%20NCTS-,Syndication,-The%20Australian%20National
#
homedir=os.environ['HOME']
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outdir", help="ouput root dir for npm packages", default=os.path.join(homedir,"data","npm"))
parser.add_argument("-t", "--tmpdir", help="tmp dir for downloaded bundles", default=os.path.join(homedir,"data","ncts-npm"))
parser.add_argument("-p", "--package_name", help="npm package name and version", default="healthterminologies.gov.au")
parser.add_argument("-v", "--package_version", help="npm package name and version", default="1.0.0")
parser.add_argument("-r", "--release", help="release version", default="20240331")


args = parser.parse_args()

# Create Raw XML file
rawxmlfile=os.path.join(args.outdir,"raw.xml")
node_folder = build_npm_folder_structure(args)

# Load client secrets from .env
load_dotenv(".env")
client_id=os.getenv("CLIENT_ID")
client_secret=os.getenv("CLIENT_SECRET")
oauth_endpoint=os.getenv("OAUTH_ENDPOINT")
oauth_scope=os.getenv("OAUTH_SCOPE")
oauth_strategy=os.getenv("OAUTH_STRATEGY")
token_endpoint=os.getenv("TOKEN_ENDPOINT")

# Fetch an access token for NCTS
auth = HTTPBasicAuth(client_id, client_secret)
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
try:
   token = oauth.fetch_token(token_url=token_endpoint, auth=auth)
   print('Token was retreived successfully')
except Exception as e:
   print('Failed to retrieve token!')
   exit

# Now we have the token access the syndication feed using curl
command = ['curl', '-H "Accept: application/xml" ' , '--location', oauth_endpoint]
result = subprocess.run(command, capture_output=True)
with open(rawxmlfile, 'wb') as x1:
    x1.write(result.stdout)
x1.close()

feed = feedparser.parse(result.stdout)

print('Entries: ',len(feed.entries))
for entry in feed.entries:
   if entry.links[0].type == "application/fhir+json":
      #print('Downloading type',entry.links[0].type,'from href:',entry.links[0].href)
      if entry.links[0].href.find(f'fhir-resource-bundle-r4-{args.release}') != -1:
         outfile=os.path.join(args.outdir,os.path.basename(entry.links[0].href))
         print("outfile: %s\n" % outfile)
         fetcher.write_json_data(entry.links[0].href,token, outfile)
         fetcher.unbundle(args,node_folder,outfile)
   