#!/usr/bin/env python3
# -*- coding: cp1252 -*-
the_world_is_flat = True
if the_world_is_flat:
     print("Be careful not to fall off!")

# this is the first comment
spam = 1  # and this is the second comment
          # ... and now a third!
text = "# This is not a comment because it's inside quotes."

width = 20
height = 5 * 9
print(width * height)

print('C:\some\name')  # here \n means newline!
print('C:\some\\name')  
print(r'C:\some\name')  # note the r before the quote

print("""\
Usage: thingy [OPTIONS]
     -h                        Display this usage message
     -H hostname               Hostname to connect to
""")

print(3 * 'un' + 'ium')

text = ('Put several strings within parentheses ' 'to have them joined together.')
print(text)

print('Py' 'thon')
print('Py'+'thon')

word = 'python'

print(word[0])
print(word[-1]) # last character
print(word[-2]) # second-last character
print(word[0:2])
print(word[:2])

#word[0] = 'J' #error ! immutable
word2 = 'J' + word[1:]
print(word2)
print(len(word))

squares = [1, 4, 9, 16, 25]
print(squares)

print(str('Zoot!'))
print(str(b'Zoot!')) #bytes
print(str(r'Zoot!'))
print("python".capitalize())
print("PYTHON".casefold())
print("PYTHON".center(20))

print("The sum of 1 + 2 is {0}".format(1+2))

#format_map
class Default(dict):
         def __missing__(self, key):return key


print('({x}, {y})'.format_map(Default(x='6')))
print('({x}, {y})'.format_map(Default(y='5')))
print('({x}, {y})'.format_map(Default(x='6', y='5')))

print('{name} was born in {country}'.format_map(Default(name='Guido',  country='France') ) )

