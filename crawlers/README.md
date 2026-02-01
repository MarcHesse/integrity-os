# Crawlers - Knowledge Acquisition

Automated crawlers for building knowledge graphs from Wikipedia and Wikidata.

---

## 📊 **Overview**

Two robust crawlers with retry logic, rate limiting, and error handling:

1. **Wikipedia Crawler** - Extracts entities and relationships from Wikipedia pages
2. **Wikidata Crawler** - Queries structured data via SPARQL

**Used in 1000-test benchmark:** Crawled 500+ Wikipedia pages across 10 domains

---

## 🕷️ **Wikipedia Crawler**

### **Features:**
- ✅ Automatic retry (3 attempts, exponential backoff)
- ✅ Rate limiting (2s delay between requests)
- ✅ URL decoding (handles C++, C#, etc.)
- ✅ Entity extraction from page links
- ✅ Category-based classification
- ✅ Relationship discovery

### **Usage:**

```python
from crawlers.wikipedia_crawler import WikipediaCrawler
from core.causal_graph import CausalGraph

# Create graph
graph = CausalGraph()

# Initialize crawler
crawler = WikipediaCrawler(graph, verbose=True)

# Crawl topic
stats = crawler.crawl_topic(
    start_page='Python',
    max_pages=10,
    max_depth=1
)

print(f"Pages crawled: {stats['pages_crawled']}")
print(f"Entities added: {stats['entities_added']}")
print(f"Relations added: {stats['relations_added']}")
```

### **Output:**
```
🕷️  Wikipedia Crawler
   Topic: Python
   Max Pages: 10, Max Depth: 1

[1/10] Python (depth 0)
[2/10] Python_(programming_language) (depth 1)
[3/10] Guido_van_Rossum (depth 1)
...

✅ Crawl Complete!
   Pages: 10
   Entities: 108
   Relations: 100
```

### **Parameters:**
- `start_page` (str): Wikipedia page title (URL-decoded automatically)
- `max_pages` (int): Maximum pages to crawl (default: 10)
- `max_depth` (int): Link depth to follow (default: 1)
- `verbose` (bool): Print progress (default: True)

### **Rate Limiting:**
- 2 seconds between requests
- Automatic retry on HTTP 429 (rate limit)
- Exponential backoff (5s, 10s, 20s)

---

## 🔍 **Wikidata Crawler**

### **Features:**
- ✅ SPARQL queries for structured data
- ✅ Property extraction (P31, P279, etc.)
- ✅ Label resolution (multilingual)
- ✅ Relationship mapping
- ✅ Rate limiting (1.5s delay)

### **Usage:**

```python
from crawlers.wikidata_crawler import WikidataCrawler

crawler = WikidataCrawler(graph, verbose=True)

# Get entity info
entity_id = 'Q28865'  # Python (programming language)
info = crawler.get_entity_info(entity_id)

print(info['label'])  # "Python"
print(info['description'])  # "high-level programming language"
print(info['properties'])  # {'instance_of': 'Q9143', ...}
```

### **Common Properties:**
- `P31`: instance of
- `P279`: subclass of
- `P50`: author
- `P571`: inception
- `P17`: country

---

## 🧪 **Testing**

### **Run All Tests:**
```bash
python test_crawlers.py
```

### **Test Wikipedia Only:**
```python
from crawlers.wikipedia_crawler import test_crawler
test_crawler()
```

### **Test Wikidata Only:**
```python
from crawlers.wikidata_crawler import test_crawler
test_crawler()
```

---

## 📋 **Benchmark Usage**

The 1000-test benchmark uses Wikipedia crawler:

```python
# From benchmark_1000_suite.py

DOMAINS = {
    'programming': {
        'topics': ['Python', 'Java', 'JavaScript', ...],
        'max_pages_per_topic': 5
    },
    'science': {
        'topics': ['Gravity', 'Evolution', 'DNA', ...],
        'max_pages_per_topic': 5
    },
    # ... 10 domains total
}

# Crawls: 10 topics × 5 pages = 50 pages per domain
# Total: 500 pages across all domains
# Result: 1,022 entities, 980 relations
```

---

## ⚙️ **Configuration**

### **Wikipedia Crawler:**
```python
WikipediaCrawler(
    graph,
    language='en',      # Wikipedia language code
    verbose=True        # Print progress
)

# Internal config:
request_delay = 2.0     # Seconds between requests
max_retries = 3         # Retry attempts
retry_delay = 5.0       # Initial retry delay
```

### **Wikidata Crawler:**
```python
WikidataCrawler(
    graph,
    verbose=True
)

# Internal config:
request_delay = 1.5     # Seconds between requests
max_retries = 3
```

---

## 🐛 **Error Handling**

### **Common Issues:**

**Problem:** `HTTP 429 - Too Many Requests`  
**Solution:** Automatic retry with exponential backoff

**Problem:** `Page not found`  
**Solution:** Logged as failed, continues with next page

**Problem:** `Connection timeout`  
**Solution:** 3 retries with 5s delay

**Problem:** `URL encoding (C++, C#)`  
**Solution:** Automatic URL decoding with `urllib.parse.unquote`

---

## 📊 **Statistics**

### **1000-Test Benchmark Crawl Stats:**

```json
{
  "pages_crawled": 99,
  "entities_added": 1022,
  "relations_added": 980
}
```

### **Per-Domain Stats:**

| Domain | Pages | Entities | Relations |
|--------|-------|----------|-----------|
| Programming | 10 | 108 | 100 |
| Science | 10 | 109 | 100 |
| Technology | 10 | 108 | 100 |
| History | 10 | 103 | 100 |
| Geography | 10 | 107 | 100 |
| Biology | 10 | 88 | 100 |
| Physics | 9 | 82 | 80 |
| Literature | 10 | 110 | 100 |
| Music | 10 | 104 | 100 |
| Art | 10 | 103 | 100 |

---

## 🔧 **Advanced Usage**

### **Custom Entity Extraction:**

```python
class CustomCrawler(WikipediaCrawler):
    def _extract_custom_data(self, page_data):
        # Add custom extraction logic
        pass
```

### **Filter by Category:**

```python
# In _crawl_page(), filter categories:
if 'Programming languages' in category_names:
    # Process differently
    pass
```

### **Custom SPARQL Queries:**

```python
query = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q9143.  # instance of programming language
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""
crawler.sparql_query(query)
```

---

## 📝 **File Structure**

```
crawlers/
├── wikipedia_crawler.py    # Wikipedia API crawler
├── wikidata_crawler.py     # Wikidata SPARQL crawler
├── test_crawlers.py        # Validation tests
└── README.md               # This file
```

---

## 🎯 **Key Features**

✅ **Robust:** Retry logic, error handling  
✅ **Respectful:** Rate limiting, user agent  
✅ **Flexible:** Configurable depth, page limits  
✅ **Tested:** 1000-test benchmark validation  
✅ **Documented:** Complete API documentation  

---

## 📧 **Contact**

Issues? Email: info@marchesse.de
