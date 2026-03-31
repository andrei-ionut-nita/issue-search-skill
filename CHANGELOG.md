# Changelog

All notable changes to the Issue Search Skill are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-31

### Added

- **Initial release** of the Issue Search Skill
- Local-first, offline-capable knowledge management system
- Complete issue capture workflow (description, symptoms, environment)
- Postmortem generation with root cause, resolution, and prevention
- Automatic Q&A generation from postmortems
- Symptom-based search with multi-factor ranking
- 14 controlled vocabulary symptoms (timeout, latency_high, api_error, etc.)
- Append-only, durable JSON/JSONL storage
- Date-partitioned filesystem organization
- Zero external dependencies (Python stdlib only)
- Comprehensive test suite (7 test categories)
- Complete documentation (5 guides + architecture)
- CLI interface with 6 main commands (capture, postmortem, search, list, show, stats)
- Performance: < 100ms search for 1000+ entries
- Quality constraints enforcing specific, non-vague root causes

### Features

#### Core Operations

- **Capture** — Record issues with symptoms and context
- **Postmortem** — Generate structured analysis from investigation
- **Search** — Retrieve solutions ranked by relevance and confidence
- **List** — Show recent issues with pagination
- **Show** — View details of specific issues or postmortems
- **Stats** — Knowledge base statistics and growth metrics

#### Ranking Algorithm

Multi-factor scoring with configurable weights:
- Symptom match (50%) — relevance to search query
- Confidence (30%) — reliability from historical usage
- Recency (10%) — newer solutions preferred
- Usage frequency (10%) — frequently-used solutions trusted more

#### Data Durability

- Append-only JSONL for logs (issues, Q&A, symptom index)
- Atomic filesystem writes
- No database required, no external dependencies
- Survives power loss, process crashes, API failures

#### Storage Organization

```
~/.knowledge_base/
├── issues/YYYY-MM-DD/           # Date-partitioned issue captures
├── postmortems/YYYY-MM-DD/      # Date-partitioned postmortems
├── qa/qa_index.jsonl            # All Q&A entries (searchable)
├── symptom_index/symptom_index.jsonl  # Symptom mappings
└── meta/                         # Future metadata
```

### Documentation

- `SKILL.md` — Skill overview and quick start
- `README.md` — Project summary
- `INSTALL_GUIDE.md` — Complete installation instructions
- `docs/QUICKSTART.md` — 5-minute setup guide
- `docs/SYSTEM_GUIDE.md` — Complete user manual (19KB)
- `docs/ARCHITECTURE.md` — System design and internals
- `docs/EXAMPLE.md` — Real-world walkthrough
- `docs/INDEX.md` — Documentation index

### Testing

- 7 comprehensive test suites (all passing)
- Schema validation tests
- Serialization round-trip tests
- Q&A generation tests
- Indexing tests
- Retrieval and ranking tests
- End-to-end workflow tests

### Performance

- Issue capture: ~1ms (O(1) JSONL append)
- Postmortem generation: ~5ms (O(1) file creation)
- Search (1000 Q&A): ~100ms (O(n) linear scan)
- List issues: ~50ms (O(d·i) with date partitioning)

Scales comfortably to 10,000+ entries without optimization.

### Code Quality

- 750 lines of core code (not counting tests)
- Clean separation of concerns (schema, utils, indexer, retriever, CLI)
- Comprehensive input validation
- Type hints throughout
- Zero external dependencies

## Future Roadmap

Planned enhancements (not in 1.0):

- **Negative signals** — Track failed attempts to avoid repeating ineffective solutions
- **Confidence decay** — Reduce confidence for unused solutions after 90 days
- **Symptom relationships** — Learn which symptoms co-occur and suggest related searches
- **Full-text search** — Search by keyword in question/answer content
- **Environment filtering** — Refine ranking by backend/OS/infrastructure
- **User feedback loop** — Rate solution helpfulness to adjust confidence
- **Related issues** — Cluster and suggest similar past issues
- **Export/reports** — Generate PDF, markdown, or JSON documentation

## Known Limitations

- Linear scan for search (scales to ~10k entries, then consider indexing)
- No built-in multi-user support (filesystem-based, single-user)
- No encryption for knowledge base (local filesystem only)
- Symptom vocabulary is fixed (prevents sprawl, can be extended)

## Support

For questions, issues, or suggestions:
- Check `docs/SYSTEM_GUIDE.md` for complete reference
- See `docs/EXAMPLE.md` for real-world walkthrough
- Run `python3 scripts/cli.py --help` for command reference
- Review `ARCHITECTURE.md` for system design details

---

**Release Information**

- **Release Date**: March 31, 2026
- **Status**: Stable (1.0.0)
- **License**: Apache License 2.0
- **Repository**: https://github.com/andrei-ionut-nita/issue-search-skill
