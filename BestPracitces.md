If you need fast and specific lookup often, nest data using section and then keep shelves flat and simple. Due to the fact HyllaDB uses Pydantic extensively for data validation, the entire contents of the shelf will be loaded each lookup or update.

However, if you are looking to get large amounts of data quickly at one time, nest data using shelves. This will allow faster retrieval of large amounts of data at once as it won't need to load multiple shelves from a section.

Note: You can always do a combination of the two strategies base on your needs. Nest data that needs fast frequent lookup in sections, keeping shelves flat and simple. Then nest data that needs to be retrieved in large amounts frequently in shelves.
