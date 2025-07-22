---
created_date: 10/07/2025
updated_date: 10/07/2025
---
# DASHBOARD

```dataview
table file.link as "Note"
from "hub"
where category and !contains(file.path, "hub/literature")
group by category
sort category asc
```

```dataview
table file.link as "File"
from "hub"
flatten file.tags as tag
where tag and !contains(file.path, "hub/literature")
group by tag
sort tag asc
```

```dataview
table
from "src"
where !contains(file.path, "src/literature")
sort file.mtime desc
limit 15
```
