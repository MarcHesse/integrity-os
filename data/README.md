# Data Directory

Benchmark results and knowledge graphs.

---

## 📊 **Contents**

### **Benchmark Results:**

**Latest:** `benchmark_1000_20260201_145905.json`

**Summary:**
- Total Tests: 1000
- Baseline Hallucinations: 337/1000 (33.7%)
- Protected Hallucinations: 5/1000 (0.5%)
- **Improvement: 99.1% Reduction**

**Format:** JSON with complete test cases, metadata, and statistics

---

## 📁 **File Structure**

```
data/
├── benchmark_1000_YYYYMMDD_HHMMSS.json    # Timestamped results
└── README.md                               # This file
```

---

## 📋 **Result File Format**

```json
{
  "metadata": {
    "timestamp": "2026-02-01T14:07:33.377371",
    "total_tests": 1000,
    "domains": [...],
    "crawl_stats": {
      "pages_crawled": 99,
      "entities_added": 1022,
      "relations_added": 980
    }
  },
  "test_cases": [...],
  "summary": {
    "baseline": {...},
    "protected": {...},
    "improvement": {...},
    "by_domain": {...}
  }
}
```

---

## 🎯 **Key Results**

| Metric | Value |
|--------|-------|
| **Pages Crawled** | 99 |
| **Entities Added** | 1,022 |
| **Relations Added** | 980 |
| **Baseline Hallucinations** | 337/1000 (33.7%) |
| **Protected Hallucinations** | 5/1000 (0.5%) |
| **Hallucinations Prevented** | 334 |
| **Relative Reduction** | **99.1%** |

---

## 📧 **Contact**

Marc Hesse - info@marchesse.de
