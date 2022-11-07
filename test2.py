list_of_args =input().split(',')
for var in list_of_args:
    print(f"self.{var} = {var}")