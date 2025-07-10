# Miller Brain Observatory Landing Page

```dataview
TABLE category AS "Section", title AS "Title", file.link AS "Note"
FROM "src"
WHERE category
SORT category asc, title asc
```