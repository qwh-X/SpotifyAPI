import re

file_path = 'open-page.html'

with open(file_path) as f:
    data = f.read()

# data = 'hello, world!'

play_matches = re.findall(r'"Play\s(.*?)"', data)
# print(play_matches)
alt_matches = re.findall(r'alt="(.*?)"', data)
# print(alt_matches)

print(set(play_matches) & set(alt_matches))

# for match in matches:
#     print(match, len(re.findall(match, data)))
