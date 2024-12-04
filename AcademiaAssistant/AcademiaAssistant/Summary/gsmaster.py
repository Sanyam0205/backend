from scholarly import scholarly
import json

class Author:
    def __init__(self, facultyname):
        self.facultyname = facultyname

    def getdata(self):
        """Fetches publication data from Google Scholar for a given faculty member."""
        search_query = scholarly.search_author(self.facultyname)
        author = scholarly.fill(next(search_query))
        return author  # Return the data directly instead of saving to a file

if __name__=='__main__':
    x = Author("Deepti Mehrotra")
    data = x.getdata()
    print(data)
