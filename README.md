# Manga App

This project is a Python-based application for searching, retrieving, and downloading manga from a specified server. Although there is no interface as of right now, it is planned somewhere in the next 500000000000 years

## Features

- **Search Manga**: Search for manga by title.
- **Get Manga Details**: Retrieve detailed information about a specific manga.
- **Get Manga Chapter**: Retrieve information about a specific chapter of a manga.
- **Download Manga**: Download manga chapters.
- **Cache Management**: Manage and clear the cache for downloaded images.
- **Sorting search**: Search all manga by state, popularity, category, genre, etc.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/wulu-epic/manga-api
    ```
2. Navigate to the project directory:
    ```sh
    cd manga-api
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Create a `.env` file in the root directory and add your server domain:
    ```env
    DOMAIN=your.server.domain
    ```

### Important
You will need to host/run the [MangaHook API](https://github.com/kiraaziz/mangahook-api/tree/main). After hosting, add the domain to your `.env` file `DOMAIN=domain`.

### Search Manga

Search for manga by title:
```python
server = Server()
query = server.search_manga("Naruto")
for manga in query.mangas:
    print(manga.title, manga.id)
```

### Get Manga Details

Retrieve detailed information about a specific manga:
```python
manga_id = "some-manga-id"
details = server.get_manga_detail(manga_id)
print(details.name, details.author, details.status)
```

### Get Manga Chapter

Retrieve information about a specific chapter of a manga:
```python
chapter_id = "some-chapter-id"
chapter = server.get_manga_chapter(manga_id, chapter_id)
print(chapter.chapter_title, chapter.manga_title)
```

### Download Manga

Download manga chapters:
```python
chapters = details.chapter_list
server.download_manga(manga_id, chapters)
```

### Cache Management

Clear the cache:
```python
server.clear_cache()
```

Get the cache size:
```python
cache_size = server.get_cache_size()
print(f"Cache size: {cache_size} MB")
```

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Acknowledgements
Thanks to this: https://github.com/kiraaziz/mangahook-api/tree/main Project wouldn't be possible without it 🙏
