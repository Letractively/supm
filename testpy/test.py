import re

url = "http://scholar.google.es/citations?view_op=view_citation&hl=es&user=w62izrcAAAAJ&citation_for_view=w62izrcAAAAJ:u-x6o8ySG0sC"


result = re.match('(.*)(:)(.*)',url).group(3)

print result