from modules.MangaAPI import *

def main():
    manga_API = Server()
    if(manga_API.is_alive() == False):
        print("Server is down. Make sure the server is on.")
        return  

    manga_list : Queries.MangaList = manga_API.get_manga_list(category=Category.Isekai, type=Sort.Popular)
    for manga in manga_list.manga_list:
        print(f"{manga.title} - {manga.image}")

    
if __name__ == "__main__":
    main()