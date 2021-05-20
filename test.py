import word_db

longdb = word_db.DB('resources\\kklong.txt')

a = longdb.get_longest_of('가')
b = longdb.get_longest_of('가', [a])

print(a, end='')

print(b, end='')
