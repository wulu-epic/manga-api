import requests, json, threading, os, random, time, math
import urllib.parse
import concurrent.futures

from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env')
config_path = Path(__file__).resolve().parents[1] / 'config.json'

with open(config_path, 'r') as file:
    config = json.load(file)

class Category(Enum):
    All = "all"
    Action = "Action"
    Adventure = "Adventure"
    Comedy = "Comedy"
    Cooking = "Cooking"
    Doujinshi = "Doujinshi"
    Drama = "Drama"
    Erotica = "Erotica"
    Fantasy = "Fantasy"
    Gender_Bender = "Gender Bender"
    Harem = "Harem"
    Historical = "Historical"
    Horror = "Horror"
    Isekai = "Isekai"
    Josei = "Josei"
    Manhua = "Manhua"
    Manwha = "Manwha"
    Martial_Arts = "Martial Arts"
    Mature = "Mature"
    Mecha = "Mecha"
    Medical = "Medical"
    One_Shot = "One Shot"
    Pornographic = "Pornographic"
    Physiological = "Physiological"
    Romance = "Romance"
    School_Life = "School Life"
    Sci_Fi = "Sci fi"
    Seinen = "Seinen"
    Shoujo_Ai = "Shoujo ai"
    Shonen = "Shonen"
    Shonen_Ai = "Shonen ai"
    Slice_Of_Life = "Slice of life"
    Smut = "Smut"
    Sports = "Sports"
    Supernatural = "Supernatural"
    Tradegy = "Tradegy"
    Webtoons = "Webtoons"
    Yuri = "Yuri"

    def __str__(self):
        return self.value

class State(Enum):
    All = "all"
    Completed = "Completed"
    Ongoing = "Ongoing"
    Dropped = "drop"
    Unknown = "unknown"

    def __str__(self):
        return self.value

class Sort(Enum):
    Newest = "newest"
    Latest = "latest"
    Popular = "topview"

    def __str__(self):
        return self.value

class Queries(object):
    class Search(object):
        class Manga():
            def __init__(self, manga_data):
                self.manga_data = manga_data

                self.id : str = None
                self.title : str = None
                self.cover_image_URL : str = None 

                self.load()
            
            def load(self):
                if self.manga_data["id"] == None:
                    raise Exception("Failed to find any data about this title")
                
                self.id = self.manga_data["id"]
                self.title = self.manga_data["title"]
                self.cover_image_URL = self.manga_data["image"]

        def __init__(self, respData : str) -> None:
            self.data = json.loads(respData)

            self.total_pages : int = 0
            self.mangas : list[self.Manga] = []

            self.load()

        def load(self):
            self.total_pages = self.data["metaData"]["totalPages"]
            if self.total_pages == 0:
                raise Exception("Failed to find any mangas that match this query.")
            
            manga_list = self.data["mangaList"]
            for manga_idx in range(0, len(manga_list)):
                manga : self.Manga = self.Manga(manga_list[manga_idx])
                self.mangas.append(manga)
    
    class DetailedManga(object):
        class Chapter:
            def __init__(self, chapter_path) -> None:
                self.id = chapter_path["id"]
                if not self.id:
                    raise Exception("Failed to find any data about this manga's chapter")
                
                self.chapter_num = self.id.replace("chapter-", "")

                self.path = chapter_path["path"]
                self.name = chapter_path["name"] 
                self.views = chapter_path["view"]
                self.creation_date = chapter_path["createdAt"]

        def __init__(self, resp) -> None:
            self.data = json.loads(resp)

            self.image_cover_URL : str = self.data["imageUrl"]
            if not self.image_cover_URL:
                raise Exception("Failed to find any data about this manga")
            
            self.name : str = self.data["name"]
            self.author : str = self.data["author"]
            self.status : str = self.data["status"]
            self.updated : str = self.data["updated"]
            self.views : str = self.data["view"]

            self.genres : list[str] = [genre for genre in self.data["genres"]]
            self.chapter_list : list[self.Chapter] = [self.Chapter(chap) for chap in self.data["chapterList"]]

    class Chapter(object):
        def __init__(self, path) -> None:
            self.path = json.loads(path)
            if not path:
                raise Exception("Failed to find any data about this chapter")

            self.manga_title = self.path["title"] 
            self.chapter_title = self.path["currentChapter"]

            self.other_chapters : list[dict[str, str]] = [{"id": chapter["id"], "name": chapter["name"]} for chapter in self.path["chapterListIds"]]
            self.image_pages : list[dict[str, str]] = [{"page_title" : page["title"], "image_URL" : page["image"]} for page in self.path["images"]]

    class MangaList(object):
        class Manga:
            def __init__(self, manga_idx) -> None:
                self.id = manga_idx["id"]
                if not self.id:
                    raise Exception("Failed to find any data about this manga")
                
                self.title = manga_idx["title"]
                self.image = manga_idx["image"]
                self.views = manga_idx["view"]

                self.description = manga_idx["description"]
                self.current_chapter = manga_idx["chapter"]

        def __init__(self, data) -> None:
            self.data = json.loads(data)
            if not self.data["mangaList"]:
                raise Exception("Failed to find any manga that matched this query")
            
            self.total_stories : int = self.data["metaData"]["totalStories"]
            self.total_pages : int = self.data["metaData"]["totalPages"]

            self.manga_list : list[self.Manga] = [self.Manga(manga) for manga in self.data["mangaList"]]

class Server(object):
    def __init__(self) -> None:
        self.HOST : str = f"http://{os.getenv("DOMAIN")}/api/"
        self.session : requests.Session = requests.Session()

    def is_alive(self) -> bool:
        try:
            self.session.get(self.HOST)
            return True
        except requests.exceptions.ConnectionError:
            return False
    
    def search_manga(self, title : str, page=1) -> Queries.Search:
        schema = f"search/{urllib.parse.quote_plus(title)}?page={str(page)}"
        resp = self.session.get(self.HOST + schema)

        query = Queries.Search(resp.text)
        return query

    def get_manga_detail(self, id) -> Queries.DetailedManga:
        schema = f'manga/{id}'
        resp = self.session.get(self.HOST + schema)

        query = Queries.DetailedManga(resp.text)
        return query
    
    def get_manga_chapter(self, id, chapter_id) -> Queries.Chapter:
        schema = f'manga/{id}/{chapter_id}'
        resp = self.session.get(self.HOST + schema)
        
        query = Queries.Chapter(resp.text)
        return query
    
    def get_manga_list(self, page=1, type="", category="", sort="", state="") -> Queries.MangaList:
        def __build_schema__() -> str:
            params = {
                "page": page,
                "type": type,
                "category": category,
                "sort": sort,
                "state": state
            }

            params = {key_value: param_value for key_value, param_value in params.items() if param_value}
            schema = f"mangaList?{urllib.parse.urlencode(params)}"
            return schema

        resp = self.session.get(self.HOST + __build_schema__())

        query = Queries.MangaList(resp.text)
        return query
    
    
    def download_image(self, url : str, save_path="./cache", image_name="", debug=False) -> str:
        file_name =  image_name + url.split("/")[-1]
        image_name = self.__sanitize__(file_name)

        if os.path.exists(save_path + "/" + image_name):
            return save_path+"/"+image_name

        image = self.session.get(url)
        if image.status_code != 200:
            print("Failed to download image: ", url)
            return "./assets/image_not_found.png"
                
        with open(save_path+"/"+image_name, "wb") as file:
            file.write(image.content)
        
        if debug:
            print("Download took", image.elapsed.total_seconds(), "seconds")

        return save_path+"/"+image_name
    
    def download_chapter(self, manga_id, chapter_id):
        chapter_data : Queries.Chapter = self.get_manga_chapter(manga_id, chapter_id)
        for page_info in chapter_data.image_pages:
            page_title = page_info['page_title']
            image_URL = page_info['image_URL']
            self.download_image(image_URL, image_name=page_title)

    def download_manga(self, manga_id, chapters: list[Queries.DetailedManga.Chapter]):
        MAX_THREADS = config.get("MAX_DOWNLOAD_THREAD_COUNT") 
        num_chapters = len(chapters)

        def download_chapter(chapter):
            print("Downloading chapter", chapter.chapter_num)
            self.download_chapter(manga_id, chapter.id)

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(download_chapter, chapter): chapter for chapter in chapters}
            print("Downloading all chapters with a total of", min(MAX_THREADS, num_chapters), "threads")
            
            for future in concurrent.futures.as_completed(futures):
                chapter = futures[future]
                try:
                    future.result() 
                except Exception as e:
                    print(f"Error downloading chapter {chapter.chapter_num}: {e}")

        end_time = time.time()
        total_time = end_time - start_time
        print("Total download time:", total_time, "seconds")

    def clear_cache(self, path="./cache") -> bool:
        for file in os.listdir(path):
            os.remove(path+"/"+file)
        
        return True

    def get_cache_size(self, path="./cache") -> float:
        total_size = sum([os.path.getsize(path+"/"+file) for file in os.listdir(path)])
        size_in_mb = total_size / (1024 * 1024)
        return size_in_mb
    
    def __sanitize__(self, string : str) -> str:
        return string.replace("/", "").replace(" ", "_").replace(":", "").replace("?", "").replace("\\", "")
    
    def __download__progress__(self, threads): 
        while any(thread.is_alive() for thread in threads):
            completed_threads = sum(not thread.is_alive() for thread in threads)
            progress = (completed_threads / len(threads)) * 100