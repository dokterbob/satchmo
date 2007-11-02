"""
Helper script to create the documentation for Satchmo
"""

import os
import string

os.environ["DJANGO_SETTINGS_MODULE"]="satchmo.settings"
pathToModelviz = "."
modelsToProcess = ["contact", "discount", "payment", "product", "shipping", "shop", "supplier", "tax"]
pathToRest = "/home/chris/python-stuff/docutils/tools"
response = string.lower(raw_input("Type 'yes' to create images of models: "))
if response == 'yes':
    print "Creating images"
    for model in modelsToProcess:
        os.system(pathToModelviz+"/graph-viz-satchmo.py" + " " + model + "> " + model + ".dot")
        os.system("dot -Tgif " + model + ".dot" + " -o" + model + ".gif")
        os.system("rm " + model + ".dot")
#Now process rest documents
print "Creating documents"
os.system(pathToRest + "/rst2html.py --stylesheet-path=./alternate-1.css " + "./satchmo-doc.txt >" + "satchmo-doc.html")
