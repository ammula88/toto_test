import os
import sys
import subprocess
import json

import toto.ssl_crypto.keys
import toto.models.layout as m
import toto.util
import toto.log as log


def wait_for_y(prompt):
  inp = False
  while inp != "":
    try:
      inp = raw_input("%s (enter)" % prompt)
      print inp
    except Exception, e:
      pass

def main():
  print """
  #############################################################################
  # Define the supply chain
  #############################################################################
  """

  # Get keys
  alice_key = toto.util.create_and_persist_or_load_key("alice")
  bob_key = toto.util.create_and_persist_or_load_key("bob")
  bob_key['keyval']['private'] = ''
  carl_key = toto.util.create_and_persist_or_load_key("carl")
  carl_key['keyval']['private'] = ''

  # Create Layout
  layout = m.Layout.read({ 
    "_type": "layout",
    "expires": "EXPIRES",
    "keys": {
        bob_key["keyid"]: bob_key,
        carl_key["keyid"]: carl_key, 
    },
    "steps": [{
        "name": "write-code",
        "material_matchrules": [],
        "product_matchrules": [["CREATE", "foo.py"]],
        "pubkeys": [bob_key["keyid"]],
        "expected_command": "vi",
      },
      {
        "name": "package",
        "material_matchrules": [
            ["MATCH", "PRODUCT", "foo.py", "FROM", "write-code"],
        ],
        "product_matchrules": [
            ["CREATE", "foo.tar.gz"],
        ],
        "pubkeys": [carl_key["keyid"]],
        "expected_command": "tar zcvf foo.tar.gz foo.py",
      }],
    "inspect": [{
        "name": "untar",
        "material_matchrules": [
            ["MATCH", "PRODUCT", "foo.tar.gz", "FROM", "package"]
        ],
        "product_matchrules": [
            ["MATCH", "PRODUCT", "foo.py", "FROM", "write-code"],
        ],
        "run": "tar xfz foo.tar.gz",
      }],
    "signatures": []
  })

  # Sign and dump layout
  layout.sign(alice_key)
  layout.dump()

  # dump alices pubkey
  alice_key['keyval']['private'] = ''
  with open("alice.pub", "wt") as fp:
      json.dump(alice_key, fp)


if __name__ == '__main__':
  main()
