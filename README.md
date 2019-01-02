Example usage:
```bash
$ python3 merger.py "/home/user/Dropbox/photos" "/home/user/Desktop/New folder" [more folders]
```

It will remove files from `/home/user/Desktop/New folder` **iff** there is an exact match (by content) in
`/home/user/Dropbox/photos` (or any other listed folder).
 
It will create json files with hash-path mappings `dir0_cache.json` and `dir1_cache.json`, a file that lists duplicates
`duplicates.json` and a file that lists removed files `removed.json`. If these files exist, it will read them instead of
creating them.
