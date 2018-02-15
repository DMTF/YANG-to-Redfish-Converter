import pyang

repo = pyang.FileRepository(input("repo: "))

context = pyang.Context(repo)

print("repo content {}".format(context.repository))
print("modules {}".format(context.modules))
print("revisions {}".format(context.revs))
