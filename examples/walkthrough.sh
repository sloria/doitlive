#doitlive shell: /bin/bash
#doitlive prompt: default
#doitlive speed: 1
#doitlive env: DOCS_URL=https://doitlive.readthedocs.io
#doitlive commentecho: true

echo 'Hello there!'

echo "Let's get started."

doitlive -h


echo "You can record sessions with doitlive record"

doitlive record -h

echo "Let's check out some themes"

doitlive themes -p

clear

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
