---
created_date: 10/07/2025
updated_date: 10/07/2025
---

# DASHBOARD

## Recently Opened Notes
```dataview
table from "notes"
where file.name != "Homepage"
sort file.mtime desc
limit 15
```

## This

```dataview
TABLE category AS "Section", title AS "Title", file.link AS "Note"
FROM "src"
WHERE category
SORT category asc, title asc
```
