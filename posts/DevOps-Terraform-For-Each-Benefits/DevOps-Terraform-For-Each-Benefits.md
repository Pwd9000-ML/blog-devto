




### Blog benefits of for_each over count

- named elements rather than numbered elements

e.g. my list = ["x", "y", "z"]

count length of list 

0 = x
1 = y
2 = z

foreach n in list n

x = x
y = y
z = z


why os this important?

When we use a dynamic config like lookup(list, x, null)

we can now use a sepcific config baed on its name.

let me show you a real world example:

app services dynamic app settings => named