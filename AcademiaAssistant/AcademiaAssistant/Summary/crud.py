import sys
sys.path.append('..')
sys.path.append('../..')
from gsmaster import Author
from Search.dbops import DB
from orchestrator import orchestrate,pubsshort,getinterests

class Profile:
    def __init__(self):
        self.gsdata = {}
        self.masterdata = {}
        self.pubsdata = []
        self.pubsdatashort = {}
        self.interests = {}
    def create(self,author):
        try:
            self.gsdata = Author(author).getdata()
            print("\nGS data recieved\n")
        except Exception as e:
            print(f"Getting error in getting GSdata: {e}")
        
        try:
            self.pubsdata,self.masterdata = orchestrate(author,self.gsdata,1)
            print("\n Publication data and Master data recieved \n")
        except Exception as e:
            print(f"Getting error in getting Publication data and Master data: {e}")
        
        try: 
            self.pubsdatashort = pubsshort(author,self.pubsdata)
            print("\n Short publication data recieved \n")
        except Exception as e:
            print(f"Error getting Short Publication data:{e}")
        
        try:
            self.interests = getinterests(author,self.gsdata)
            print("\n Interests data recieved \n")
        except Exception as e:
            print(f"Error getting Interests:{e}")
        db = DB().getcollection(author)
        db.addpublications(self.pubsdata)

    def searcher(self,author,query):
        db = DB().getcollection(author)
        return db.get_contexts(query)
    def update(self,author,data):
        pass
    def delete(self,author):
        pass

if __name__=="__main__":
    author = input("Please enter the author name\n")
    mode = input("Please enter the mode - index or query\n")
    if mode=="index":
        profile = Profile()
        profile.create(author)
    elif mode=="query":
        query = input("Please enter your query\n")
        profile = Profile()
        results =  profile.searcher(author,query)
        print(results)
    else:
        print("Please enter the correct mode\n")
    