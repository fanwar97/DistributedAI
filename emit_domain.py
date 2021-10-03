import os
path = "list_test_domain"
f = open(path, "r")
domain = f.readlines()
f.close()
# domain = "google.com"
for line in domain:
    os.system("nslookup " + line)