import shelve


class SimpleClass:
    def __init__(self, attribute: str) -> None:
        print("Init method called")
        self.attribute: str = attribute

    def append_to_attribute(self, string: str) -> None:
        print("Append method called")
        self.attribute += string


# Create an instance of the class
instance = SimpleClass("Hello World!")

# Store the instance in a shelve file
with shelve.open("my_shelve") as db:
    db["my_instance"] = instance

# Retrieve the instance from the shelve file
with shelve.open("my_shelve") as db:
    print("Retrieving instance from shelve...")
    retrieved_instance: SimpleClass = db["my_instance"]
    print("Retrieved attribute:", retrieved_instance.attribute)
    print("Retrieved instance type:", type(retrieved_instance))
    retrieved_instance.append_to_attribute(" Goodbye World!")
    db["my_instance"] = retrieved_instance

# Retrieve the instance from the shelve file
with shelve.open("my_shelve") as db:
    print("Again retrieving instance from shelve...")
    new_retrieved_instance: SimpleClass = db["my_instance"]
    print("Retrieved attribute:", new_retrieved_instance.attribute)
    print("Retrieved instance type:", type(new_retrieved_instance))
