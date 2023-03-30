#doitlive shell: /bin/bash
#doitlive prompt: default
#doitlive speed: 2
#doitlive commentecho: true

echo 'Hello there!'

echo "Let's get started. There is an anchor named 'anchor1 after this string."

#doitlive anchor: start

echo "There is an anchor 'start' before this line. Any commands before it will not have been executed, if --from_anchor was set to 'start' at the command line"

doitlive -h

# doitlive anchor: themes

doitlive themes -p

clear

# doitlive anchor: python

# And now for something completely different

echo 'We can even enter a Python console'

```python
list = [2, 4, 6, 8]
sum = 0
for num in list:
    sum = sum + num

print("The sum is: {sum}".format(sum=sum))
```

#doitlive speed: 2
echo 'Pretty neat, eh?'

echo 'Did you notice that the speed changed?'

echo 'For full docs, check out:' $DOCS_URL
